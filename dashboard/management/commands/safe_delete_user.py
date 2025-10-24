from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.db import transaction
from dashboard.models import Notificacao


class Command(BaseCommand):
    help = 'Exclui um usuário de forma segura, limpando suas referências primeiro'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='ID do usuário a ser excluído')
        parser.add_argument(
            '--force',
            action='store_true',
            help='Força a exclusão sem confirmação',
        )

    def handle(self, *args, **options):
        user_id = options['user_id']
        force = options['force']
        
        try:
            # Verificar se o usuário existe
            try:
                user = User.objects.get(id=user_id)
                self.stdout.write(f"👤 Usuário encontrado: {user.username} ({user.email})")
            except User.DoesNotExist:
                raise CommandError(f'Usuário com ID {user_id} não encontrado')
            
            # Verificar se é superuser
            if user.is_superuser:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  ATENÇÃO: {user.username} é um superusuário!')
                )
                if not force:
                    confirm = input("Tem certeza que deseja excluir um superusuário? (digite 'CONFIRMO'): ")
                    if confirm != 'CONFIRMO':
                        self.stdout.write(self.style.ERROR('Exclusão cancelada'))
                        return
            
            # Limpar referências
            self.stdout.write("🧹 Limpando referências do usuário...")
            
            with transaction.atomic():
                # 1. Notificações
                notificacoes_count = Notificacao.objects.filter(usuario=user).count()
                if notificacoes_count > 0:
                    Notificacao.objects.filter(usuario=user).update(usuario=None)
                    self.stdout.write(f"✅ {notificacoes_count} notificações atualizadas")
                
                # 2. Verificar se é admin de loja
                try:
                    from lojas.models import Loja
                    lojas_admin = Loja.objects.filter(admin_user=user)
                    if lojas_admin.exists():
                        self.stdout.write(
                            self.style.ERROR(
                                f'❌ ERRO: Usuário é administrador de {lojas_admin.count()} loja(s):'
                            )
                        )
                        for loja in lojas_admin:
                            self.stdout.write(f'   - {loja.nome}')
                        self.stdout.write('Transfira a administração antes de excluir o usuário.')
                        return
                except ImportError:
                    pass
                
                # 3. Desativar funcionário se existir
                try:
                    from lojas.models import Funcionario
                    funcionario = Funcionario.objects.filter(user=user).first()
                    if funcionario:
                        funcionario.ativo = False
                        funcionario.save()
                        self.stdout.write(f"✅ Funcionário da loja '{funcionario.loja.nome}' desativado")
                except ImportError:
                    pass
                
                # 4. Desativar sessões ativas
                try:
                    from usuarios.models import SessaoAtiva
                    sessoes_ativas = SessaoAtiva.objects.filter(user=user, ativa=True)
                    if sessoes_ativas.exists():
                        sessoes_ativas.update(ativa=False)
                        self.stdout.write(f"✅ {sessoes_ativas.count()} sessões ativas desativadas")
                except ImportError:
                    pass
                
                # Confirmação final
                if not force:
                    self.stdout.write(
                        self.style.WARNING(f'\n⚠️  Confirma a exclusão do usuário "{user.username}"?')
                    )
                    self.stdout.write('Esta ação não pode ser desfeita!')
                    confirm = input("Digite 'sim' para confirmar: ").lower().strip()
                    if confirm != 'sim':
                        self.stdout.write(self.style.ERROR('Exclusão cancelada'))
                        return
                
                # Excluir usuário
                username = user.username
                user.delete()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Usuário "{username}" excluído com sucesso!')
                )
                
        except Exception as e:
            raise CommandError(f'Erro ao excluir usuário: {e}')
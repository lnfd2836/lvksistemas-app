from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lojas.models import Loja
from modulos.models import TipoLoja
import uuid


class Command(BaseCommand):
    help = 'Associa usuários à loja FATESA'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nome de usuário específico')
        parser.add_argument('--todos', action='store_true', help='Associar todos os usuários com perfil FATESA')

    def handle(self, *args, **options):
        try:
            tipo_controle = TipoLoja.objects.get(nome='controle_qualidade')
        except TipoLoja.DoesNotExist:
            self.stdout.write(self.style.ERROR("Tipo de loja 'controle_qualidade' não encontrado!"))
            return
        
        username = options.get('username')
        todos = options.get('todos')
        
        if username:
            self._processar_usuario(username, tipo_controle)
        elif todos:
            self._processar_todos_usuarios(tipo_controle)
        else:
            self._listar_usuarios_sem_loja()

    def _processar_usuario(self, username, tipo_controle):
        """Processa um usuário específico"""
        try:
            user = User.objects.get(username=username)
            self._criar_loja_para_usuario(user, tipo_controle)
            self.stdout.write(
                self.style.SUCCESS(f'Usuário {username} processado com sucesso!')
            )
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário {username} não encontrado!')
            )

    def _processar_todos_usuarios(self, tipo_controle):
        """Processa todos os usuários com perfil FATESA"""
        from avaliacao_qualidade.models import PerfilUsuario
        
        perfis = PerfilUsuario.objects.all()
        count = 0
        
        for perfil in perfis:
            user = perfil.user
            self._criar_loja_para_usuario(user, tipo_controle)
            count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'\n{count} usuários processados!')
        )

    def _criar_loja_para_usuario(self, user, tipo_controle):
        """Cria ou obtém loja para um usuário"""
        try:
            # Verifica se já tem loja
            if hasattr(user, 'loja_admin') and user.loja_admin:
                self.stdout.write(f"✅ {user.username} - Loja já existia")
                return
            
            # Cria nova loja
            loja = Loja.objects.create(
                nome=f"Controle de qualidade - {user.username}",
                endereco='FATESA',
                telefone='(00) 0000-0000',
                email=user.email or 'admin@fatesa.edu.br',
                tipo_loja=tipo_controle,
                admin_user=user,
                cnpj=f'{user.id:014d}'  # CNPJ único baseado no ID do usuário
            )
            self.stdout.write(f"✅ {user.username} - Nova loja criada")
            
        except Exception as e:
            self.stdout.write(f"❌ {user.username} - Erro: {str(e)}")

    def _listar_usuarios_sem_loja(self):
        """Lista usuários sem loja associada"""
        users_sem_loja = []
        for user in User.objects.all():
            if not hasattr(user, 'loja_admin') or not user.loja_admin:
                users_sem_loja.append(user)
        
        if users_sem_loja:
            self.stdout.write("Usuários sem loja associada:")
            for user in users_sem_loja:
                self.stdout.write(f"- {user.username}")
            
            self.stdout.write("\nUse --todos para associar todos os usuários com perfil FATESA")
            self.stdout.write("Ou --username=NOME para associar um usuário específico")
        else:
            self.stdout.write("Todos os usuários já possuem loja associada.")
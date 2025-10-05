from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from usuarios.models import SessaoAtiva
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Gerencia sessões ativas dos usuários'

    def add_arguments(self, parser):
        parser.add_argument(
            '--listar',
            action='store_true',
            help='Lista todas as sessões ativas'
        )
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Remove sessões expiradas'
        )
        parser.add_argument(
            '--usuario',
            type=str,
            help='Nome do usuário para gerenciar sessões'
        )
        parser.add_argument(
            '--invalidar-todas',
            action='store_true',
            help='Invalida todas as sessões de um usuário (exceto Super Admins)'
        )
        parser.add_argument(
            '--super-admin',
            action='store_true',
            help='Mostra apenas sessões de Super Admins'
        )

    def handle(self, *args, **options):
        if options['listar']:
            self.listar_sessoes(options)
        elif options['limpar']:
            self.limpar_sessoes_expiradas()
        elif options['invalidar_todas'] and options['usuario']:
            self.invalidar_sessoes_usuario(options['usuario'])
        else:
            self.stdout.write(
                self.style.ERROR('Use --help para ver as opções disponíveis')
            )

    def listar_sessoes(self, options):
        """Lista todas as sessões ativas"""
        queryset = SessaoAtiva.objects.filter(ativa=True)
        
        if options['usuario']:
            queryset = queryset.filter(user__username=options['usuario'])
        
        if options['super_admin']:
            queryset = queryset.filter(is_super_admin=True)
        
        queryset = queryset.order_by('-data_login')
        
        self.stdout.write(
            self.style.SUCCESS(f'\n=== SESSÕES ATIVAS ({queryset.count()}) ===\n')
        )
        
        for sessao in queryset:
            status = "🟢 ATIVA" if sessao.ativa else "🔴 INATIVA"
            tipo = "👑 SUPER ADMIN" if sessao.is_super_admin else "👤 USUÁRIO"
            
            self.stdout.write(
                f"{tipo} | {status}\n"
                f"  👤 Usuário: {sessao.user.username}\n"
                f"  🌐 IP: {sessao.ip_address}\n"
                f"  📱 User Agent: {sessao.user_agent[:50]}...\n"
                f"  📅 Login: {sessao.data_login.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"  ⏰ Última Atividade: {sessao.ultima_atividade.strftime('%d/%m/%Y %H:%M:%S')}\n"
                f"  🔑 Session Key: {sessao.session_key[:20]}...\n"
                f"  {'='*50}\n"
            )

    def limpar_sessoes_expiradas(self):
        """Remove sessões expiradas"""
        self.stdout.write('Limpando sessões expiradas...')
        
        # Remove sessões com mais de 24 horas de inatividade
        limite = datetime.now() - timedelta(hours=24)
        sessoes_removidas = SessaoAtiva.objects.filter(
            ultima_atividade__lt=limite,
            ativa=True
        ).update(ativa=False)
        
        self.stdout.write(
            self.style.SUCCESS(f'Sessões expiradas removidas: {sessoes_removidas}')
        )

    def invalidar_sessoes_usuario(self, username):
        """Invalida todas as sessões de um usuário"""
        try:
            user = User.objects.get(username=username)
            
            sessoes_invalidadas = SessaoAtiva.objects.filter(
                user=user,
                ativa=True
            ).update(ativa=False)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Sessões invalidadas para {username}: {sessoes_invalidadas}'
                )
            )
            
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário {username} não encontrado')
            )

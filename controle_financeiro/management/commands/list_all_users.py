"""
Comando Django para listar todos os usuários do sistema
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Lista todos os usuários do sistema'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--superusers-only',
            action='store_true',
            help='Mostrar apenas super usuários'
        )
        
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='Mostrar apenas usuários ativos'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.HTTP_INFO("=== LISTA DE USUÁRIOS DO SISTEMA ==="))
        
        # Filtros
        users = User.objects.all()
        
        if options['superusers_only']:
            users = users.filter(is_superuser=True)
            self.stdout.write("Filtro: Apenas super usuários")
        
        if options['active_only']:
            users = users.filter(is_active=True)
            self.stdout.write("Filtro: Apenas usuários ativos")
        
        users = users.order_by('username')
        
        self.stdout.write(f"\nTotal encontrado: {users.count()} usuários")
        self.stdout.write("=" * 80)
        
        for user in users:
            # Status
            status_parts = []
            if user.is_superuser:
                status_parts.append("SUPER")
            if user.is_staff:
                status_parts.append("STAFF")
            if user.is_active:
                status_parts.append("ATIVO")
            else:
                status_parts.append("INATIVO")
            
            status = " | ".join(status_parts)
            
            # Informações do usuário
            self.stdout.write(f"👤 {user.username}")
            self.stdout.write(f"   📧 Email: {user.email}")
            self.stdout.write(f"   🏷️  Status: {status}")
            self.stdout.write(f"   📅 Criado: {user.date_joined.strftime('%d/%m/%Y %H:%M')}")
            self.stdout.write(f"   🔑 Último login: {user.last_login.strftime('%d/%m/%Y %H:%M') if user.last_login else 'Nunca'}")
            
            # Verificar se tem loja associada
            try:
                from lojas.models import Loja
                loja = Loja.objects.filter(admin_user=user).first()
                if loja:
                    self.stdout.write(f"   🏪 Loja: {loja.nome}")
            except:
                pass
            
            self.stdout.write("")
        
        # Estatísticas
        self.stdout.write("=" * 80)
        self.stdout.write(self.style.HTTP_INFO("📊 ESTATÍSTICAS:"))
        
        total = User.objects.count()
        ativos = User.objects.filter(is_active=True).count()
        inativos = User.objects.filter(is_active=False).count()
        superusers = User.objects.filter(is_superuser=True).count()
        staff = User.objects.filter(is_staff=True).count()
        
        self.stdout.write(f"Total de usuários: {total}")
        self.stdout.write(f"Usuários ativos: {ativos}")
        self.stdout.write(f"Usuários inativos: {inativos}")
        self.stdout.write(f"Super usuários: {superusers}")
        self.stdout.write(f"Staff: {staff}")
        
        # Sugestões
        self.stdout.write("\n" + "=" * 80)
        self.stdout.write(self.style.HTTP_INFO("💡 DICAS:"))
        self.stdout.write("• Para resetar senhas: python manage.py reset_admin_passwords")
        self.stdout.write("• Para criar super usuário: python manage.py createsuperuser")
        self.stdout.write("• Para testar login: python manage.py shell")
        
        if superusers == 0:
            self.stdout.write(
                self.style.WARNING("⚠️ ATENÇÃO: Nenhum super usuário encontrado!")
            )
            self.stdout.write("Execute: python manage.py createsuperuser")
        
        self.stdout.write("=" * 80)
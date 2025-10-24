from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lojas.models import Loja
from modulos.models import TipoLoja


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
            # Associar usuário específico
            try:
                user = User.objects.get(username=username)
                # Criar nova loja para cada usuário ou usar a existente
                user_loja, created = Loja.objects.get_or_create(
                    admin_user=user,
                    defaults={
                        'nome': f"Controle de qualidade - {user.username}",
                        'endereco': 'FATESA',
                        'telefone': '(00) 0000-0000',
                        'email': user.email or 'admin@fatesa.edu.br',
                        'tipo_loja': tipo_controle
                    }
                )
                if created:
                    self.stdout.write(f"✅ Nova loja criada para {user.username}")
                else:
                    self.stdout.write(f"✅ Loja já existia para {user.username}")
                    
                self.stdout.write(
                    self.style.SUCCESS(f'Usuário {username} associado à loja FATESA!')
                )
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Usuário {username} não encontrado!')
                )
        
        elif todos:
            # Associar todos os usuários com perfil FATESA
            from avaliacao_qualidade.models import PerfilUsuario
            
            perfis = PerfilUsuario.objects.all()
            count = 0
            
            for perfil in perfis:
                user = perfil.user
                # Criar nova loja para cada usuário ou usar a existente
                user_loja, created = Loja.objects.get_or_create(
                    admin_user=user,
                    defaults={
                        'nome': f"Controle de qualidade - {user.username}",
                        'endereco': 'FATESA',
                        'telefone': '(00) 0000-0000',
                        'email': user.email or 'admin@fatesa.edu.br',
                        'tipo_loja': tipo_controle
                    }
                )
                count += 1
                if created:
                    self.stdout.write(f"✅ {user.username} - Nova loja criada")
                else:
                    self.stdout.write(f"✅ {user.username} - Loja já existia")
            
            self.stdout.write(
                self.style.SUCCESS(f'\n{count} usuários processados!')
            )
        
        else:
            # Listar usuários sem loja
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
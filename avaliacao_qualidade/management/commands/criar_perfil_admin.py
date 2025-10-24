from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from avaliacao_qualidade.models import PerfilUsuario


class Command(BaseCommand):
    help = 'Cria perfil FATESA para usuários existentes'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Nome de usuário')
        parser.add_argument('--tipo', type=str, choices=['diretoria', 'coordenacao', 'professor', 'secretaria'], 
                          default='diretoria', help='Tipo de perfil')

    def handle(self, *args, **options):
        username = options.get('username')
        tipo = options.get('tipo', 'diretoria')
        
        if not username:
            # Listar usuários sem perfil
            users_sem_perfil = []
            for user in User.objects.all():
                try:
                    user.perfil_fatesa
                except PerfilUsuario.DoesNotExist:
                    users_sem_perfil.append(user)
            
            if users_sem_perfil:
                self.stdout.write("Usuários sem perfil FATESA:")
                for user in users_sem_perfil:
                    self.stdout.write(f"- {user.username} ({user.email})")
                
                username = input("\nDigite o nome de usuário para criar perfil: ")
            else:
                self.stdout.write("Todos os usuários já possuem perfil FATESA.")
                return

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuário {username} não encontrado!')
            )
            return

        # Verificar se já tem perfil
        try:
            perfil = user.perfil_fatesa
            self.stdout.write(
                self.style.WARNING(f'Usuário {username} já possui perfil: {perfil.get_tipo_perfil_display()}')
            )
            return
        except PerfilUsuario.DoesNotExist:
            pass

        # Criar perfil
        nome_completo = user.first_name + ' ' + user.last_name if user.first_name else user.username
        
        perfil = PerfilUsuario.objects.create(
            user=user,
            tipo_perfil=tipo,
            nome_completo=nome_completo
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Perfil criado para {username}!\n'
                f'Tipo: {perfil.get_tipo_perfil_display()}\n'
                f'Nome: {perfil.nome_completo}'
            )
        )
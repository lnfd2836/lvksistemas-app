"""
Comando para migrar usuários existentes para o novo sistema de perfis
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from lojas.models import Loja
from email_credentials.models import ExtendedUserProfile, LojaUserProfile
from email_credentials.database_router import LojasDatabaseRouter
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migra usuários existentes para o sistema de perfis estendidos'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular operações sem executar'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forçar migração mesmo se perfis já existirem'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Migrar apenas usuário específico'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== MIGRAÇÃO DE USUÁRIOS EXISTENTES ===')
        )
        
        # Filtrar usuários
        if options['user_id']:
            try:
                users = [User.objects.get(id=options['user_id'])]
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Usuário com ID {options["user_id"]} não encontrado')
                )
                return
        else:
            users = User.objects.all()
        
        self.stdout.write(f'Processando {users.count()} usuário(s)...')
        
        stats = {
            'total': 0,
            'super_admins': 0,
            'loja_admins': 0,
            'loja_users': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for user in users:
            result = self.migrate_user(user, options)
            stats['total'] += 1
            stats[result] += 1
        
        self.print_stats(stats)
    
    def migrate_user(self, user, options):
        """Migra um usuário específico"""
        
        self.stdout.write(f'\n👤 Migrando usuário: {user.username}')
        
        if options['dry_run']:
            self.stdout.write('   [DRY RUN] Simulando migração...')
        
        # Verificar se já tem perfil estendido
        if hasattr(user, 'extended_profile') and not options['force']:
            self.stdout.write('   ⏭️ Usuário já tem perfil estendido, pulando...')
            return 'skipped'
        
        try:
            # Determinar tipo de usuário
            user_type = self.determine_user_type(user)
            self.stdout.write(f'   📋 Tipo determinado: {user_type}')
            
            # Encontrar loja associada
            loja = self.find_associated_loja(user)
            if loja:
                self.stdout.write(f'   🏪 Loja associada: {loja.nome}')
            
            if not options['dry_run']:
                # Criar perfil estendido
                self.create_extended_profile(user, user_type, loja)
                
                # Criar perfil da loja se necessário
                if loja and user_type in ['loja_admin', 'loja_user']:
                    self.create_loja_profile(user, loja, user_type)
            
            self.stdout.write('   ✅ Migração concluída')
            return user_type.replace('_', '_')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ❌ Erro na migração: {str(e)}')
            )
            return 'errors'
    
    def determine_user_type(self, user):
        """Determina o tipo do usuário baseado em suas características"""
        
        # Super usuário
        if user.is_superuser:
            return 'super_admins'
        
        # Admin de loja
        if hasattr(user, 'loja_admin'):
            return 'loja_admins'
        
        # Verificar se tem perfil FATESA
        if hasattr(user, 'perfil_fatesa'):
            return 'loja_users'
        
        # Verificar grupos
        user_groups = user.groups.values_list('name', flat=True)
        
        if any('admin' in group.lower() for group in user_groups):
            return 'loja_admins'
        
        # Default para usuário de loja
        return 'loja_users'
    
    def find_associated_loja(self, user):
        """Encontra a loja associada ao usuário"""
        
        # Admin de loja
        if hasattr(user, 'loja_admin'):
            return user.loja_admin
        
        # Perfil FATESA
        if hasattr(user, 'perfil_fatesa') and user.perfil_fatesa.loja_associada:
            return user.perfil_fatesa.loja_associada
        
        # Tentar encontrar por outros critérios
        # Por exemplo, se o username contém o nome da loja
        for loja in Loja.objects.filter(status='ativa'):
            loja_slug = loja.nome.lower().replace(' ', '_')
            if loja_slug in user.username.lower():
                return loja
        
        return None
    
    def create_extended_profile(self, user, user_type, loja):
        """Cria perfil estendido no banco principal"""
        
        # Mapear tipos
        type_mapping = {
            'super_admins': 'super_admin',
            'loja_admins': 'loja_admin',
            'loja_users': 'loja_user'
        }
        
        profile, created = ExtendedUserProfile.objects.get_or_create(
            user=user,
            defaults={
                'user_type': type_mapping[user_type],
                'has_provisional_password': False,  # Senhas existentes são permanentes
                'password_changed_at': timezone.now(),
                'associated_loja': loja,
                'database_alias': LojasDatabaseRouter.get_loja_database_alias(loja.id) if loja else 'default'
            }
        )
        
        if not created:
            # Atualizar perfil existente
            profile.user_type = type_mapping[user_type]
            if loja and not profile.associated_loja:
                profile.associated_loja = loja
                profile.database_alias = LojasDatabaseRouter.get_loja_database_alias(loja.id)
            profile.save()
        
        return profile
    
    def create_loja_profile(self, user, loja, user_type):
        """Cria perfil no banco específico da loja"""
        
        try:
            db_alias = LojasDatabaseRouter.get_loja_database_alias(loja.id)
            
            # Determinar perfil de acesso
            if user_type == 'loja_admins':
                access_profile = 'admin'
                permissions = {
                    'can_manage_users': True,
                    'can_view_reports': True,
                    'can_manage_settings': True,
                    'can_create_evaluations': True
                }
            else:
                # Tentar determinar pelo perfil FATESA existente
                access_profile = 'user'
                permissions = {}
                
                if hasattr(user, 'perfil_fatesa'):
                    fatesa_profile = user.perfil_fatesa
                    if fatesa_profile.tipo_perfil == 'diretoria':
                        access_profile = 'diretoria'
                        permissions = {'can_manage_users': True, 'can_view_reports': True}
                    elif fatesa_profile.tipo_perfil == 'coordenacao':
                        access_profile = 'coordenacao'
                        permissions = {'can_view_reports': True}
                    elif fatesa_profile.tipo_perfil == 'professor':
                        access_profile = 'professor'
                        permissions = {'can_view_own_evaluations': True}
                    elif fatesa_profile.tipo_perfil == 'secretaria':
                        access_profile = 'secretaria'
                        permissions = {'can_create_evaluations': True}
            
            # Criar perfil da loja
            loja_profile, created = LojaUserProfile.objects.using(db_alias).get_or_create(
                user_id=user.id,
                defaults={
                    'username': user.username,
                    'loja_access_profile': access_profile,
                    'permissions': permissions,
                    'settings': {}
                }
            )
            
            return loja_profile
            
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f'   ⚠️ Erro ao criar perfil da loja: {str(e)}')
            )
            return None
    
    def print_stats(self, stats):
        """Imprime estatísticas da migração"""
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('ESTATÍSTICAS DA MIGRAÇÃO')
        self.stdout.write('='*50)
        
        self.stdout.write(f'Total de usuários processados: {stats["total"]}')
        self.stdout.write(f'Super Admins migrados: {stats["super_admins"]}')
        self.stdout.write(f'Admins de Loja migrados: {stats["loja_admins"]}')
        self.stdout.write(f'Usuários de Loja migrados: {stats["loja_users"]}')
        self.stdout.write(f'Usuários pulados: {stats["skipped"]}')
        self.stdout.write(f'Erros: {stats["errors"]}')
        
        if stats['errors'] == 0:
            self.stdout.write(
                self.style.SUCCESS('\n✅ Migração concluída com sucesso!')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'\n⚠️ Migração concluída com {stats["errors"]} erro(s)')
            )
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db import transaction
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.shortcuts import render
from dashboard.models import Notificacao


class SafeUserAdmin(BaseUserAdmin):
    """
    Admin personalizado para User com exclusão segura
    """
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:user_id>/safe-delete/',
                self.admin_site.admin_view(self.safe_delete_view),
                name='auth_user_safe_delete',
            ),
        ]
        return custom_urls + urls
    
    def safe_delete_view(self, request, user_id):
        """
        View para exclusão segura de usuário
        """
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            messages.error(request, f'Usuário com ID {user_id} não encontrado.')
            return HttpResponseRedirect(reverse('admin:auth_user_changelist'))
        
        if request.method == 'POST':
            if 'confirm' in request.POST:
                try:
                    with transaction.atomic():
                        # Limpar referências
                        self._clean_user_references(user)
                        
                        # Excluir usuário
                        username = user.username
                        user.delete()
                        
                        messages.success(
                            request, 
                            f'Usuário "{username}" excluído com sucesso!'
                        )
                        
                except Exception as e:
                    messages.error(request, f'Erro ao excluir usuário: {e}')
                
                return HttpResponseRedirect(reverse('admin:auth_user_changelist'))
            
            elif 'cancel' in request.POST:
                return HttpResponseRedirect(reverse('admin:auth_user_change', args=[user_id]))
        
        # Verificar dependências
        dependencies = self._check_dependencies(user)
        
        context = {
            'title': f'Exclusão Segura - {user.username}',
            'user_to_delete': user,
            'dependencies': dependencies,
            'has_blocking_dependencies': any(dep['blocking'] for dep in dependencies),
            'opts': self.model._meta,
        }
        
        return render(request, 'admin/auth/user/safe_delete.html', context)
    
    def _check_dependencies(self, user):
        """
        Verifica dependências do usuário
        """
        dependencies = []
        
        # Notificações
        notificacoes_count = Notificacao.objects.filter(usuario=user).count()
        if notificacoes_count > 0:
            dependencies.append({
                'model': 'Notificações',
                'count': notificacoes_count,
                'action': 'Serão definidas como NULL',
                'blocking': False
            })
        
        # Verificar se é admin de loja
        try:
            from lojas.models import Loja
            lojas_admin = Loja.objects.filter(admin_user=user)
            if lojas_admin.exists():
                dependencies.append({
                    'model': 'Lojas (Administrador)',
                    'count': lojas_admin.count(),
                    'action': 'BLOQUEANTE - Transfira a administração primeiro',
                    'blocking': True,
                    'details': [loja.nome for loja in lojas_admin]
                })
        except ImportError:
            pass
        
        # Funcionário
        try:
            from lojas.models import Funcionario
            funcionario = Funcionario.objects.filter(user=user, ativo=True).first()
            if funcionario:
                dependencies.append({
                    'model': 'Funcionário',
                    'count': 1,
                    'action': f'Será desativado da loja "{funcionario.loja.nome}"',
                    'blocking': False
                })
        except ImportError:
            pass
        
        # Sessões ativas
        try:
            from usuarios.models import SessaoAtiva
            sessoes_count = SessaoAtiva.objects.filter(user=user, ativa=True).count()
            if sessoes_count > 0:
                dependencies.append({
                    'model': 'Sessões Ativas',
                    'count': sessoes_count,
                    'action': 'Serão desativadas',
                    'blocking': False
                })
        except ImportError:
            pass
        
        return dependencies
    
    def _clean_user_references(self, user):
        """
        Limpa referências do usuário antes da exclusão
        """
        # Notificações
        Notificacao.objects.filter(usuario=user).update(usuario=None)
        
        # Desativar funcionário
        try:
            from lojas.models import Funcionario
            Funcionario.objects.filter(user=user).update(ativo=False)
        except ImportError:
            pass
        
        # Desativar sessões
        try:
            from usuarios.models import SessaoAtiva
            SessaoAtiva.objects.filter(user=user, ativa=True).update(ativa=False)
        except ImportError:
            pass
    
    def get_actions(self, request):
        """
        Remove a ação padrão de delete e adiciona a nossa
        """
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
    def has_delete_permission(self, request, obj=None):
        """
        Sempre retorna False para usar nossa exclusão personalizada
        """
        return False


# Desregistrar o admin padrão e registrar o nosso
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, SafeUserAdmin)
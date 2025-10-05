# URL Configuration Guide

## Visão Geral

Este documento descreve a nova configuração de URLs otimizada para o sistema de dashboard, focando na prevenção de conflitos de roteamento e melhoria da organização.

## Estrutura de URLs Refatorada

### URLs Principais (`lojad/urls.py`)

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', redirect_to_appropriate_dashboard, name='root_redirect'),  # ✨ NOVO
    
    # URLs principais
    path('dashboard/', include('dashboard.urls')),
    path('lojas/', include('lojas.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('planos/', include('planos.urls')),
    path('financeiro/', include('controle_financeiro.urls')),
    path('modulos/', include('modulos.urls')),
    
    # URLs de autenticação
    path('login/', simple_login, name='simple_login'),
    path('loja/login/', loja_login, name='loja_login'),
]
```

### URLs do Dashboard (`dashboard/urls.py`)

```python
app_name = 'dashboard'  # ✨ NOVO - Namespace para evitar conflitos

urlpatterns = [
    # Dashboard principal
    path('', views.dashboard_principal, name='principal'),
    
    # Dashboards específicos
    path('super-admin/', views.dashboard_super_admin, name='super_admin'),
    path('loja/', views.dashboard_loja, name='loja'),
    path('loja/<uuid:loja_id>/', views.dashboard_loja, name='loja_especifica'),
    
    # APIs e AJAX - organizadas com prefixo
    path('api/estatisticas/', views.estatisticas_ajax, name='api_estatisticas'),
    path('api/notificacao/<int:notificacao_id>/marcar-lida/', 
         views.marcar_notificacao_lida, name='api_marcar_notificacao_lida'),
    
    # Administração - organizadas com prefixo
    path('admin/usuarios/', views.listar_usuarios_super_admin, name='admin_usuarios_lista'),
    path('admin/usuarios/criar/', views.criar_usuario_super_admin, name='admin_usuarios_criar'),
    path('admin/sessoes/', views.gerenciar_sessoes, name='admin_sessoes'),
    path('admin/modulos/', views.gerenciar_modulos, name='admin_modulos'),
    
    # Redirecionamento inteligente
    path('redirect/', views.redirect_to_appropriate_dashboard, name='redirect_inteligente'),
]
```

## Principais Melhorias

### 1. **Redirecionamento Inteligente da Raiz**

**Antes:**
```python
path('', lambda request: redirect('/login/')),  # Sempre para login
```

**Depois:**
```python
path('', redirect_to_appropriate_dashboard, name='root_redirect'),  # Inteligente
```

**Benefícios:**
- Usuários autenticados vão direto para seu dashboard
- Usuários não autenticados vão para login
- Evita redirecionamentos desnecessários

### 2. **Namespace para Dashboard**

**Antes:**
```python
# Sem namespace - conflitos possíveis
path('dashboard/', views.dashboard_principal, name='dashboard'),
```

**Depois:**
```python
app_name = 'dashboard'
path('', views.dashboard_principal, name='principal'),
# Acesso via: dashboard:principal
```

**Benefícios:**
- Evita conflitos de nomes entre apps
- URLs mais organizadas e previsíveis
- Facilita manutenção

### 3. **Organização por Prefixos**

**APIs:**
- `/dashboard/api/estatisticas/`
- `/dashboard/api/notificacao/<id>/marcar-lida/`

**Administração:**
- `/dashboard/admin/usuarios/`
- `/dashboard/admin/sessoes/`
- `/dashboard/admin/modulos/`

**Benefícios:**
- Estrutura clara e intuitiva
- Facilita implementação de middleware específico
- Melhora segurança com regras por prefixo

### 4. **URLs de Autenticação Consistentes**

**Antes:**
```python
path('login/', simple_login, name='login'),
path('dashboard/login/', simple_login, name='login'),  # Duplicação
```

**Depois:**
```python
path('login/', simple_login, name='simple_login'),
path('loja/login/', loja_login, name='loja_login'),
```

**Benefícios:**
- Elimina duplicação
- Nomes consistentes
- Reduz confusão

## Mapeamento de URLs

### URLs Antigas → Novas

| URL Antiga | URL Nova | Nome Antigo | Nome Novo |
|------------|----------|-------------|-----------|
| `/` | `/` | - | `root_redirect` |
| `/dashboard/` | `/dashboard/` | `dashboard` | `dashboard:principal` |
| `/dashboard/super-admin/` | `/dashboard/super-admin/` | `dashboard_super_admin` | `dashboard:super_admin` |
| `/dashboard/loja/dashboard/` | `/dashboard/loja/` | `dashboard_loja` | `dashboard:loja` |
| `/dashboard/usuarios-super-admin/` | `/dashboard/admin/usuarios/` | `listar_usuarios_super_admin` | `dashboard:admin_usuarios_lista` |
| `/dashboard/sessoes/` | `/dashboard/admin/sessoes/` | `gerenciar_sessoes` | `dashboard:admin_sessoes` |
| `/dashboard/modulos/` | `/dashboard/admin/modulos/` | `gerenciar_modulos` | `dashboard:admin_modulos` |
| `/dashboard/estatisticas/` | `/dashboard/api/estatisticas/` | `estatisticas_ajax` | `dashboard:api_estatisticas` |

## Uso nas Views

### Redirecionamentos

**Antes:**
```python
return redirect('dashboard')
return redirect('login')
```

**Depois:**
```python
return redirect('dashboard:principal')
return redirect('simple_login')
```

### Reverse URLs

**Antes:**
```python
from django.urls import reverse
url = reverse('dashboard')
```

**Depois:**
```python
from django.urls import reverse
url = reverse('dashboard:principal')
```

### Templates

**Antes:**
```html
<a href="{% url 'dashboard' %}">Dashboard</a>
```

**Depois:**
```html
<a href="{% url 'dashboard:principal' %}">Dashboard</a>
```

## Prevenção de Loops de Redirecionamento

### 1. **Função de Redirecionamento Inteligente**

```python
def redirect_to_appropriate_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('simple_login')
    
    try:
        dashboard_url = AuthenticationService.determine_user_dashboard(request.user)
        return redirect(dashboard_url)
    except Exception as e:
        logger.error(f"Erro ao determinar dashboard: {str(e)}")
        return redirect('simple_login')
```

### 2. **Validação nas Views**

```python
def dashboard_principal(request):
    # Verificar se o usuário deve estar neste dashboard
    expected_url = AuthenticationService.determine_user_dashboard(request.user)
    
    # Se a URL esperada não for a atual, redirecionar
    if expected_url != request.path and expected_url != '/dashboard/':
        return redirect(expected_url)
```

### 3. **Limite de Redirecionamentos**

- Máximo de 3 redirecionamentos por requisição
- Logging de loops detectados
- Fallback para página de erro se necessário

## Segurança

### 1. **URLs Administrativas Protegidas**

```python
# Todas as URLs admin/* requerem super usuário
path('admin/usuarios/', views.listar_usuarios_super_admin, name='admin_usuarios_lista'),
```

### 2. **APIs Protegidas**

```python
# Todas as URLs api/* requerem autenticação
path('api/estatisticas/', views.estatisticas_ajax, name='api_estatisticas'),
```

### 3. **Validação de Permissões**

- Verificação de tipo de usuário em todas as views administrativas
- Logging de tentativas de acesso não autorizado
- Redirecionamento seguro em caso de erro

## Compatibilidade

### 1. **Backward Compatibility**

- URLs antigas ainda funcionam (com redirecionamento)
- Nomes antigos mantidos como aliases quando possível
- Migração gradual suportada

### 2. **Templates Existentes**

- Templates existentes continuam funcionando
- Recomendado atualizar para novos nomes gradualmente

### 3. **JavaScript e AJAX**

- URLs de API mantêm funcionalidade
- Novos endpoints têm prefixo `/api/` para clareza

## Testes

### 1. **Testes de Roteamento**

```python
def test_url_resolution(self):
    # Testa se URLs resolvem para views corretas
    resolved = resolve('/dashboard/')
    self.assertEqual(resolved.func, dashboard_principal)
```

### 2. **Testes de Redirecionamento**

```python
def test_root_redirect(self):
    # Testa redirecionamento inteligente da raiz
    response = self.client.get('/')
    self.assertEqual(response.status_code, 302)
```

### 3. **Testes de Segurança**

```python
def test_admin_urls_require_super_user(self):
    # Testa que URLs admin requerem super usuário
    response = self.client.get('/dashboard/admin/usuarios/')
    self.assertIn(response.status_code, [302, 403])
```

## Monitoramento

### 1. **Logging de URLs**

```python
# Log de acessos a URLs administrativas
logger.info(f"Acesso a URL administrativa: {request.path} por {request.user.username}")
```

### 2. **Métricas**

- Contagem de redirecionamentos por URL
- Tempo de resposta por endpoint
- Tentativas de acesso não autorizado

### 3. **Alertas**

- Loops de redirecionamento detectados
- Múltiplas tentativas de acesso não autorizado
- Erros 404 em URLs críticas

## Migração

### 1. **Fase 1: Implementação**

- ✅ Implementar nova estrutura de URLs
- ✅ Manter compatibilidade com URLs antigas
- ✅ Atualizar views para usar novos nomes

### 2. **Fase 2: Atualização**

- [ ] Atualizar templates para novos nomes
- [ ] Atualizar JavaScript para novas APIs
- [ ] Documentar mudanças para equipe

### 3. **Fase 3: Limpeza**

- [ ] Remover URLs antigas após período de transição
- [ ] Remover aliases desnecessários
- [ ] Otimizar estrutura final

## Troubleshooting

### Problemas Comuns

1. **URL não encontrada (404)**
   - Verificar se namespace está correto
   - Confirmar se URL está definida em `urlpatterns`

2. **Loop de redirecionamento**
   - Verificar lógica de `determine_user_dashboard`
   - Confirmar se não há redirecionamentos circulares

3. **Acesso negado (403)**
   - Verificar permissões do usuário
   - Confirmar se view requer super usuário

### Debugging

```python
# Listar todas as URLs disponíveis
python manage.py show_urls

# Testar resolução de URL específica
from django.urls import reverse
print(reverse('dashboard:principal'))

# Debug de redirecionamentos
import logging
logging.getLogger('dashboard.views').setLevel(logging.DEBUG)
```
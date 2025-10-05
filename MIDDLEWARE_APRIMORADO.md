# Middleware de Autenticação Aprimorado

## Visão Geral

O middleware de autenticação aprimorado (`ImprovedAuthenticationMiddleware`) substitui o `SessaoUnicaMiddleware` anterior com melhorias significativas em:

- **Prevenção de loops de redirecionamento**
- **Gerenciamento robusto de sessões**
- **Tratamento de erros aprimorado**
- **Logging detalhado para debugging**
- **Performance otimizada**

## Funcionalidades Principais

### 1. Prevenção de Loops de Redirecionamento

- Detecta loops diretos (mesmo URL repetido)
- Identifica padrões circulares (A→B→A→B)
- Quebra loops automaticamente com logout forçado
- Limite configurável de redirecionamentos (padrão: 3)

### 2. Gerenciamento de Sessões

- Validação robusta de sessões ativas
- Criação automática de sessões quando necessário
- Limpeza periódica de sessões expiradas
- Suporte a sessão única por usuário

### 3. Tratamento de Erros

- Recuperação elegante de erros de banco de dados
- Fallback para comportamento seguro em caso de falhas
- Logging detalhado para debugging
- Mensagens de erro claras para usuários

## Configuração

### Middleware Configurado

O middleware já está configurado em `lojad/settings.py`:

```python
MIDDLEWARE = [
    # ... outros middlewares ...
    'usuarios.improved_middleware.ImprovedAuthenticationMiddleware',
    # ... outros middlewares ...
]
```

### Logging Configurado

O sistema de logging está configurado para capturar eventos de autenticação:

```python
LOGGING = {
    'loggers': {
        'usuarios.services': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'usuarios.improved_middleware': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
    },
}
```

## Como Usar

### 1. Reiniciar o Servidor

Após a configuração, reinicie o servidor Django:

```bash
python manage.py runserver
```

### 2. Monitorar Logs

Os logs de autenticação são salvos em:
- Console (desenvolvimento)
- `logs/authentication.log` (produção local)
- Heroku logs (produção)

### 3. Testar Funcionalidades

#### Teste de Login Normal
1. Acesse `/login/`
2. Faça login com credenciais válidas
3. Verifique se é redirecionado para o dashboard correto

#### Teste de Prevenção de Loops
1. Tente acessar URLs protegidas sem autenticação
2. Verifique se não há loops infinitos
3. Confirme que mensagens de erro são exibidas

#### Teste de Sessão Única
1. Faça login em um navegador
2. Faça login com o mesmo usuário em outro navegador
3. Verifique se a primeira sessão é invalidada

## Serviços Disponíveis

### AuthenticationService

Gerencia lógica de autenticação centralizada:

```python
from usuarios.services import AuthenticationService

# Determina dashboard apropriado para usuário
dashboard_url = AuthenticationService.determine_user_dashboard(user)

# Verifica se pode acessar dashboard de loja
can_access, error_msg = AuthenticationService.can_access_store_dashboard(user, store)

# Obtém loja associada ao usuário
store = AuthenticationService.get_user_store(user)
```

### SessionService

Gerencia sessões de usuários:

```python
from usuarios.services import SessionService

# Cria nova sessão para usuário
success = SessionService.create_user_session(request, user)

# Valida sessão atual
is_valid = SessionService.validate_session(request)

# Invalida todas as sessões do usuário
SessionService.invalidate_user_sessions(user)
```

### RedirectLoopPreventionService

Previne loops de redirecionamento:

```python
from usuarios.services import RedirectLoopPreventionService

# Executa redirecionamento seguro
response = RedirectLoopPreventionService.safe_redirect(request, target_url)

# Verifica se redirecionamento é seguro
is_safe = RedirectLoopPreventionService.is_safe_redirect(request, target_url)
```

## Monitoramento e Debugging

### Logs Importantes

Monitore estes tipos de log:

```
INFO - Nova sessão criada para usuário username
WARNING - Sessão inválida para usuário username, forçando logout
WARNING - Loop de redirecionamento detectado para usuário username
ERROR - Erro ao validar sessão: detalhes do erro
```

### Métricas de Performance

O middleware inclui otimizações:

- Limpeza de sessões a cada 100 requisições (1%)
- Cache de validações de sessão
- Verificação otimizada de caminhos excluídos

### Debugging

Para debugging detalhado, ajuste o nível de log:

```python
LOGGING['loggers']['usuarios.improved_middleware']['level'] = 'DEBUG'
```

## Solução de Problemas

### Problema: Loops de Redirecionamento

**Sintomas**: Usuário fica preso entre login e dashboard

**Solução**:
1. Verifique logs para padrões de redirecionamento
2. Confirme que URLs estão configuradas corretamente
3. Verifique se usuário tem loja associada (se necessário)

### Problema: Sessões Não Funcionam

**Sintomas**: Usuário é deslogado constantemente

**Solução**:
1. Verifique configuração de sessões no Django
2. Confirme que `SESSION_COOKIE_AGE` está adequado
3. Verifique se há erros de banco de dados nos logs

### Problema: Performance Lenta

**Sintomas**: Autenticação demora muito

**Solução**:
1. Verifique se limpeza de sessões não está muito frequente
2. Otimize consultas de banco de dados
3. Considere usar cache para validações

## Migração do Middleware Antigo

### Diferenças Principais

| Recurso | Middleware Antigo | Middleware Novo |
|---------|------------------|-----------------|
| Prevenção de loops | ❌ | ✅ |
| Tratamento de erros | Básico | Robusto |
| Logging | Mínimo | Detalhado |
| Performance | Padrão | Otimizada |
| Configurabilidade | Limitada | Extensiva |

### Compatibilidade

O novo middleware é totalmente compatível com:
- Modelos existentes (`SessaoAtiva`)
- Views existentes
- Templates existentes
- Configurações de URL

## Configurações Avançadas

### Personalizar Limites

```python
# Em usuarios/improved_middleware.py
class ImprovedAuthenticationMiddleware:
    def __init__(self, get_response):
        # Personalizar caminhos excluídos
        self.excluded_paths = [
            '/admin/',
            '/api/',  # Adicionar novos caminhos
            # ...
        ]
```

### Personalizar Prevenção de Loops

```python
# Em usuarios/services.py
class RedirectLoopPreventionService:
    MAX_REDIRECTS = 5  # Aumentar limite se necessário
```

## Testes

### Executar Testes

```bash
# Teste simples de importação e configuração
python test_middleware_simple.py

# Testes unitários (quando migrations estiverem funcionando)
python manage.py test usuarios.tests.test_improved_middleware
```

### Testes Manuais

1. **Teste de Login**: Faça login e logout várias vezes
2. **Teste de Múltiplas Sessões**: Login simultâneo em vários navegadores
3. **Teste de URLs Protegidas**: Acesse URLs sem autenticação
4. **Teste de Erros**: Simule erros de banco de dados

## Suporte

Para problemas ou dúvidas:

1. Verifique os logs de autenticação
2. Execute `python test_middleware_simple.py`
3. Consulte a documentação do Django sobre middleware
4. Revise o código em `usuarios/improved_middleware.py` e `usuarios/services.py`

## Próximas Melhorias

Funcionalidades planejadas:

- [ ] Cache Redis para sessões
- [ ] Métricas de autenticação
- [ ] Rate limiting para login
- [ ] Autenticação 2FA
- [ ] API de monitoramento
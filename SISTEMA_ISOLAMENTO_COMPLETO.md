# Sistema de Isolamento Completo por Loja

## Visão Geral

O sistema de isolamento garante que cada loja tenha acesso apenas aos seus próprios dados, usando bancos de dados separados e controle de acesso rigoroso.

## Componentes Principais

### 1. Router de Banco de Dados (`database_router_isolado.py`)

**Classe:** `LojaIsoladaDBRouter`

- **Função:** Direciona operações de banco para o banco correto baseado no contexto da loja
- **Modelos do Sistema:** Sempre usam banco `default`
- **Modelos de Loja:** Usam banco específico `loja_{id}`

**Modelos do Sistema (banco principal):**
- `auth.user`, `auth.group`, `auth.permission`
- `lojas.loja`, `lojas.loginpersonalizado`
- `usuarios.usuario`, `planos.plano`
- `email_credentials.*`

**Modelos de Loja (bancos isolados):**
- `controle_financeiro.*`
- `avaliacao_qualidade.*`
- `modulos.*`

### 2. Middleware de Isolamento (`middleware_login_isolado.py`)

**Classes:**
- `LoginIsoladoMiddleware`: Controla acesso por login personalizado
- `DatabaseIsolationMiddleware`: Define contexto de banco por loja

**Funcionalidades:**
- Valida acesso baseado na URL de login personalizado
- Define contexto da loja na thread
- Impede acesso cruzado entre lojas
- Força logout em caso de violação

### 3. Serviço de Isolamento (`services/isolamento_service.py`)

**Classe:** `IsolamentoService`

**Métodos principais:**
- `validate_user_loja_access()`: Valida se usuário pode acessar loja
- `get_user_loja_context()`: Obtém contexto da loja do usuário
- `execute_with_loja_context()`: Executa função no contexto da loja
- `get_loja_queryset_filter()`: Filtros para QuerySets isolados

### 4. Gerenciador de Contexto (`database_router_isolado.py`)

**Classe:** `LojaContextManager`

```python
# Uso do context manager
with LojaContextManager(loja_id):
    # Operações executadas no contexto da loja
    dados = MinhaModel.objects.all()  # Automaticamente isolado
```

## Configuração

### 1. Settings.py

```python
# Middleware (ordem importante)
MIDDLEWARE = [
    # ... outros middlewares ...
    'lojas.middleware_login_isolado.LoginIsoladoMiddleware',
    'lojas.middleware_login_isolado.DatabaseIsolationMiddleware',
    # ... outros middlewares ...
]

# Database Routers
DATABASE_ROUTERS = [
    'lojas.database_router_isolado.LojaIsoladaDBRouter',
    'email_credentials.db_router.LojaDBRouter',  # Compatibilidade
]
```

### 2. Configuração de Bancos

Os bancos são configurados dinamicamente:
- `default`: Banco principal do sistema
- `loja_{id}`: Banco específico de cada loja

## Uso em Views

### 1. Decorador de Isolamento

```python
from lojas.services.isolamento_service import require_loja_isolation

@login_required
@require_loja_isolation
def minha_view(request):
    # Automaticamente executada no contexto da loja do usuário
    dados = MinhaModel.objects.all()  # Dados isolados
    return render(request, 'template.html', {'dados': dados})
```

### 2. Execução Manual no Contexto

```python
def minha_funcao():
    # Função que precisa de dados isolados
    return MinhaModel.objects.all()

# Executar no contexto da loja do usuário
dados = IsolamentoService.execute_with_loja_context(
    request.user, minha_funcao
)
```

### 3. Context Manager

```python
from lojas.database_router_isolado import LojaContextManager

with LojaContextManager(loja_id):
    # Todas as operações de banco usam o banco da loja
    dados = MinhaModel.objects.all()
    novo_objeto = MinhaModel.objects.create(...)
```

## Tipos de Usuário

### 1. Super Admins
- **Acesso:** Todos os dados do sistema
- **Banco:** Sempre `default`
- **Login:** Apenas via login principal (`/login/`)
- **Restrição:** NÃO podem usar login personalizado de loja

### 2. Admins de Loja
- **Acesso:** Apenas dados da sua loja
- **Banco:** `loja_{id}` específico
- **Login:** Via login personalizado (`/login/{loja_url}/`)
- **Isolamento:** Completo por banco de dados

### 3. Funcionários
- **Acesso:** Apenas dados da loja onde trabalham
- **Banco:** `loja_{id}` da loja empregadora
- **Login:** Via login personalizado da loja
- **Isolamento:** Mesmo nível dos admins de loja

## Comandos de Gerenciamento

### Setup Inicial
```bash
python manage.py setup_isolamento --setup
```

### Validação
```bash
python manage.py setup_isolamento --validate
```

### Migrações
```bash
python manage.py setup_isolamento --migrate
```

### Status
```bash
python manage.py setup_isolamento --status
```

## Testes

### Script de Teste
```bash
python scripts/test_isolamento.py
```

### Testes Realizados:
1. **Isolamento de Banco:** Verifica contextos de thread
2. **Validação de Acesso:** Testa permissões por usuário
3. **Serviço de Isolamento:** Valida funcionalidades do serviço

## Segurança

### 1. Validações Implementadas
- Usuário só acessa dados da sua loja
- Super admins não podem usar login de loja
- Logout automático em violações
- Contexto de thread isolado

### 2. Prevenção de Vazamentos
- Router de banco impede acesso cruzado
- Middleware valida cada requisição
- Context manager garante isolamento
- Filtros automáticos em QuerySets

### 3. Auditoria
- Logs detalhados de acesso
- Rastreamento de violações
- Monitoramento de contexto
- Validação contínua

## Fluxo de Acesso

### 1. Login Personalizado
```
1. Usuário acessa /login/{loja_url}/
2. Middleware identifica loja pela URL
3. Define contexto da loja na thread
4. Valida se usuário pode acessar loja
5. Redireciona para dashboard isolado
```

### 2. Operações de Banco
```
1. Model.objects.all() é chamado
2. Router verifica contexto da thread
3. Direciona para banco correto (loja_{id})
4. Retorna apenas dados da loja
```

### 3. Validação Contínua
```
1. Cada requisição passa pelo middleware
2. Verifica se usuário ainda pode acessar loja
3. Valida integridade do contexto
4. Força logout se necessário
```

## Monitoramento

### 1. Logs Importantes
- `lojas.middleware_login_isolado`: Acesso e violações
- `lojas.database_router_isolado`: Operações de banco
- `lojas.services.isolamento_service`: Validações

### 2. Métricas
- Bancos configurados vs lojas ativas
- Tentativas de acesso negado
- Contextos de thread ativos
- Performance por loja

## Troubleshooting

### 1. Problemas Comuns

**Erro: "Banco loja_X não encontrado"**
```bash
python manage.py setup_isolamento --setup --loja-id X
```

**Usuário não consegue acessar dados**
```bash
python manage.py setup_isolamento --validate
```

**Dados aparecendo de outras lojas**
- Verificar se router está configurado
- Validar contexto da thread
- Checar logs do middleware

### 2. Debug

**Verificar contexto atual:**
```python
from lojas.database_router_isolado import get_current_loja_id, get_current_loja_db
print(f"Loja: {get_current_loja_id()}")
print(f"Banco: {get_current_loja_db()}")
```

**Validar isolamento:**
```python
from lojas.services.isolamento_service import IsolamentoService
status = IsolamentoService.get_isolation_status()
print(status)
```

## Considerações de Performance

### 1. Otimizações
- Context manager reutiliza conexões
- Router cache configurações
- Middleware pula URLs desnecessárias
- Lazy loading de bancos

### 2. Limitações
- Cada loja precisa de banco separado
- Overhead de validação por requisição
- Complexidade de manutenção
- Migrações em múltiplos bancos

## Conclusão

O sistema de isolamento garante segurança total entre lojas, usando:
- **Isolamento físico:** Bancos separados
- **Controle de acesso:** Validação rigorosa
- **Contexto de thread:** Isolamento automático
- **Auditoria completa:** Logs e monitoramento

Este sistema é adequado para ambientes multi-tenant onde a segurança e isolamento de dados são críticos.
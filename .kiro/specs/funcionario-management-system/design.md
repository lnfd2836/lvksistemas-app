# Design Document

## Overview

O sistema de gerenciamento de funcionários será integrado ao dashboard da loja, permitindo que administradores cadastrem, gerenciem e controlem permissões de funcionários baseado no tipo específico de loja. O sistema utilizará a arquitetura Django existente e se integrará com os modelos de autenticação e tipos de loja já implementados.

## Architecture

### Componentes Principais

1. **Models Layer**: Novos modelos para funcionários e tipos de funcionários
2. **Views Layer**: Views para CRUD de funcionários e gerenciamento de permissões
3. **Templates Layer**: Interface web responsiva para gerenciamento
4. **Authentication Layer**: Integração com sistema de autenticação existente
5. **Permissions Layer**: Sistema de permissões baseado em tipos de funcionário

### Integração com Sistema Existente

- Utiliza o modelo `User` do Django para autenticação
- Integra com `TipoLoja` para definir tipos de funcionários específicos
- Conecta com `Loja` para associar funcionários às lojas
- Aproveita o sistema de middleware de autenticação existente

## Components and Interfaces

### 1. Models

#### TipoFuncionario
```python
class TipoFuncionario(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    tipo_loja = models.ForeignKey(TipoLoja)
    permissoes = models.JSONField()  # Armazena permissões específicas
    ativo = models.BooleanField(default=True)
```

#### Funcionario
```python
class Funcionario(models.Model):
    user = models.OneToOneField(User)
    loja = models.ForeignKey(Loja)
    tipo_funcionario = models.ForeignKey(TipoFuncionario)
    codigo_funcionario = models.CharField(unique=True)
    data_admissao = models.DateField()
    salario = models.DecimalField()  # Opcional
    ativo = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True)
```

### 2. Views Structure

#### FuncionarioListView
- Lista todos os funcionários da loja
- Filtros por tipo e status
- Paginação para grandes volumes

#### FuncionarioCreateView
- Formulário de cadastro
- Validação de dados
- Criação automática de usuário Django

#### FuncionarioUpdateView
- Edição de dados do funcionário
- Alteração de tipo e permissões
- Histórico de alterações

#### FuncionarioDetailView
- Visualização completa dos dados
- Histórico de atividades
- Relatórios individuais

### 3. URL Structure

```
/dashboard/funcionarios/
├── lista/                    # Lista de funcionários
├── novo/                     # Cadastro de funcionário
├── <id>/                     # Detalhes do funcionário
├── <id>/editar/             # Edição do funcionário
├── <id>/desativar/          # Desativação do funcionário
├── tipos/                   # Gerenciamento de tipos
└── permissoes/              # Configuração de permissões
```

## Data Models

### Tipos de Funcionários por Loja

#### Lanchonete
- **Atendente**: Atendimento ao cliente, pedidos
- **Cozinheiro**: Preparo de alimentos, controle de estoque de ingredientes
- **Gerente**: Acesso total, relatórios, configurações
- **Caixa**: Vendas, recebimentos, fechamento de caixa

#### Loja de Conveniência
- **Atendente**: Atendimento geral, vendas básicas
- **Repositor**: Controle de estoque, reposição de produtos
- **Gerente**: Gestão completa da loja
- **Caixa**: Operações de venda e pagamento
- **Segurança**: Monitoramento, relatórios de segurança

#### Loja de Roupas
- **Vendedor**: Vendas, atendimento ao cliente
- **Provador**: Assistência em provadores, organização
- **Gerente**: Gestão completa, compras, relatórios
- **Caixa**: Operações financeiras
- **Visual Merchandising**: Organização visual, vitrines

#### Supermercado
- **Operador de Caixa**: Operações de checkout
- **Repositor**: Reposição de produtos, organização
- **Açougueiro**: Seção de carnes, atendimento especializado
- **Padeiro**: Seção de panificação
- **Gerente**: Gestão geral, relatórios
- **Segurança**: Monitoramento, prevenção de perdas

#### Loja de Tintas
- **Vendedor Técnico**: Consultoria técnica, vendas especializadas
- **Colorista**: Preparação de cores, mistura de tintas
- **Gerente**: Gestão completa, compras técnicas
- **Caixa**: Operações financeiras
- **Estoquista**: Controle de estoque especializado

#### Eletrônicos
- **Vendedor Técnico**: Vendas especializadas, consultoria
- **Técnico em Eletrônicos**: Assistência técnica, reparos
- **Gerente**: Gestão completa, relacionamento com fornecedores
- **Caixa**: Operações financeiras
- **Estoquista**: Controle de estoque, logística

### Permissions Matrix

```json
{
  "gerente": {
    "dashboard": ["read", "write"],
    "vendas": ["read", "write", "delete"],
    "produtos": ["read", "write", "delete"],
    "clientes": ["read", "write", "delete"],
    "funcionarios": ["read", "write"],
    "relatorios": ["read", "write"],
    "configuracoes": ["read", "write"]
  },
  "caixa": {
    "dashboard": ["read"],
    "vendas": ["read", "write"],
    "produtos": ["read"],
    "clientes": ["read", "write"],
    "relatorios": ["read"]
  },
  "vendedor": {
    "dashboard": ["read"],
    "vendas": ["read", "write"],
    "produtos": ["read"],
    "clientes": ["read", "write"]
  }
}
```

## Error Handling

### Validation Errors
- Email duplicado: Verificação antes da criação
- Tipo incompatível: Validação de tipo de funcionário vs tipo de loja
- Dados obrigatórios: Validação de campos required

### Business Logic Errors
- Funcionário já existe: Verificação de duplicidade
- Loja inativa: Não permitir cadastro em lojas inativas
- Limite de funcionários: Verificar limites do plano (se aplicável)

### System Errors
- Falha na criação de usuário: Rollback da transação
- Erro de permissões: Log e notificação ao administrador
- Falha de email: Continuar processo mas notificar erro

## Testing Strategy

### Unit Tests
- Validação de modelos
- Lógica de permissões
- Criação automática de usuários
- Filtros por tipo de loja

### Integration Tests
- Fluxo completo de cadastro
- Autenticação de funcionários
- Aplicação de permissões
- Integração com dashboard existente

### UI Tests
- Formulários de cadastro
- Listagem e filtros
- Responsividade mobile
- Fluxos de edição e desativação

### Security Tests
- Controle de acesso por loja
- Validação de permissões
- Prevenção de escalação de privilégios
- Proteção contra CSRF
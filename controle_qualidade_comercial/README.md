# Sistema de Controle de Qualidade Comercial

## Visão Geral

O Sistema de Controle de Qualidade Comercial é uma aplicação Django completa para gerenciamento de produtos, vendas, controle de qualidade e reclamações de clientes. O sistema oferece funcionalidades abrangentes para empresas que precisam monitorar a qualidade de seus produtos e processos comerciais.

## Funcionalidades Principais

### 📊 Dashboard Interativo
- Métricas em tempo real
- Gráficos de vendas diárias
- Top produtos mais vendidos
- Distribuição de reclamações por tipo
- Evolução da qualidade ao longo do tempo

### 📦 Gestão de Produtos
- CRUD completo de produtos
- Controle de estoque com alertas
- Categorização de produtos
- Gestão de fornecedores
- Códigos de barras e SKUs

### 💰 Controle de Vendas
- Registro de vendas
- Múltiplas formas de pagamento
- Controle de itens por venda
- Relatórios de vendas
- Histórico completo

### 🔍 Controle de Qualidade
- Inspeções de qualidade
- Sistema de notas (1-5)
- Critérios de avaliação:
  - Aparência visual
  - Integridade da embalagem
  - Conformidade com especificação
- Ações corretivas
- Histórico de inspeções

### 📞 Gestão de Reclamações
- Registro de reclamações de clientes
- Sistema de protocolos automáticos
- Controle de status e prioridades
- Tempo de resolução
- Avaliação de satisfação

### 🎯 Metas de Qualidade
- Definição de metas
- Acompanhamento de progresso
- Diferentes tipos de metas:
  - Aprovação de produtos
  - Satisfação do cliente
  - Redução de reclamações
  - Tempo de resolução

### 📈 Relatórios e Análises
- Relatórios de vendas
- Relatórios de qualidade
- Estatísticas gerais
- Exportação em CSV
- Backup completo em JSON

## Estrutura do Projeto

```
controle_qualidade_comercial/
├── models.py              # Modelos de dados
├── views.py               # Views e lógica de negócio
├── urls.py                # Configuração de rotas
├── admin.py               # Interface administrativa
├── apps.py                # Configuração da aplicação
├── migrations/            # Migrações do banco de dados
├── templates/             # Templates HTML
│   └── controle_qualidade_comercial/
│       ├── base.html
│       ├── dashboard.html
│       ├── produtos/
│       ├── vendas/
│       ├── qualidade/
│       ├── reclamacoes/
│       ├── metas/
│       ├── categorias/
│       ├── fornecedores/
│       └── relatorios/
├── static/                # Arquivos estáticos
│   └── controle_qualidade_comercial/
│       ├── css/
│       ├── js/
│       └── img/
└── README.md
```

## Modelos de Dados

### Principais Entidades

1. **ProdutoComercial**
   - Informações básicas do produto
   - Preços e estoque
   - Categoria e fornecedor
   - Status ativo/inativo

2. **VendaComercial**
   - Dados da venda
   - Cliente e vendedor
   - Forma de pagamento
   - Status da venda

3. **ItemVenda**
   - Itens individuais da venda
   - Quantidade e preços
   - Subtotais

4. **ControleQualidade**
   - Inspeções de qualidade
   - Notas por critério
   - Status de aprovação
   - Ações corretivas

5. **ReclamacaoCliente**
   - Dados da reclamação
   - Protocolo automático
   - Status e prioridade
   - Resolução e satisfação

6. **MetaQualidade**
   - Definição de metas
   - Progresso atual
   - Períodos de avaliação

## Instalação e Configuração

### Pré-requisitos
- Python 3.8+
- Django 4.0+
- PostgreSQL (recomendado)

### Passos de Instalação

1. **Clone o repositório**
```bash
git clone <repository-url>
cd lvksistemas-app
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure o banco de dados**
```bash
python manage.py makemigrations controle_qualidade_comercial
python manage.py migrate
```

4. **Crie um superusuário**
```bash
python manage.py createsuperuser
```

5. **Execute o servidor**
```bash
python manage.py runserver
```

## Configuração de URLs

Adicione ao `urls.py` principal do projeto:

```python
from django.urls import path, include

urlpatterns = [
    # ... outras URLs
    path('controle-qualidade/', include('controle_qualidade_comercial.urls')),
]
```

## Uso do Sistema

### Acesso Inicial
1. Acesse `/controle-qualidade/` no navegador
2. Faça login com suas credenciais
3. Verifique se o usuário está associado a uma loja do tipo 'dashboard_comercial'

### Fluxo Básico de Uso

1. **Configuração Inicial**
   - Criar categorias de produtos
   - Cadastrar fornecedores
   - Configurar metas de qualidade

2. **Gestão de Produtos**
   - Cadastrar produtos
   - Definir estoques mínimos
   - Associar categorias e fornecedores

3. **Registro de Vendas**
   - Criar vendas
   - Adicionar itens
   - Definir forma de pagamento

4. **Controle de Qualidade**
   - Realizar inspeções
   - Avaliar critérios
   - Registrar ações corretivas

5. **Gestão de Reclamações**
   - Registrar reclamações
   - Acompanhar resolução
   - Avaliar satisfação

## APIs Disponíveis

### APIs do Dashboard
- `/api/metricas/` - Métricas gerais
- `/api/vendas-diarias/` - Vendas dos últimos 7 dias
- `/api/top-produtos/` - Produtos mais vendidos
- `/api/reclamacoes-tipo/` - Distribuição de reclamações
- `/api/evolucao-qualidade/` - Evolução da qualidade

### APIs de Relatórios
- `/api/relatorio-vendas/` - Relatório de vendas
- `/api/relatorio-qualidade/` - Relatório de qualidade

### APIs Utilitárias
- `/ajax/buscar-produtos/` - Busca de produtos
- `/ajax/buscar-vendas/` - Busca de vendas

## Recursos Técnicos

### Frontend
- Bootstrap 5.3
- jQuery 3.6
- Chart.js para gráficos
- Font Awesome para ícones
- Máscaras de input
- Validação em tempo real

### Backend
- Django 4.0+
- PostgreSQL
- APIs REST
- Sistema de permissões
- Validações de dados
- Tratamento de erros

### Funcionalidades Avançadas
- Auto-save em formulários
- Busca em tempo real
- Exportação de dados
- Backup automático
- Sistema de notificações
- Responsividade mobile

## Segurança

- Autenticação obrigatória
- Verificação de permissões por loja
- Proteção CSRF
- Validação de dados
- Sanitização de inputs

## Performance

- Queries otimizadas com select_related
- Cache de métricas
- Paginação automática
- Lazy loading de imagens
- Compressão de assets

## Manutenção

### Backup
- Backup automático via interface
- Exportação em JSON
- Exportação em CSV por entidade

### Logs
- Logs de ações importantes
- Rastreamento de erros
- Auditoria de alterações

### Monitoramento
- Métricas de performance
- Alertas de estoque baixo
- Notificações de sistema

## Suporte

Para suporte técnico:
- Email: suporte@lvksistemas.com
- Telefone: (11) 9999-9999
- Site: www.lvksistemas.com

## Licença

Este sistema é propriedade da LVK Sistemas. Todos os direitos reservados.

## Changelog

### Versão 1.0.0 (2024-10-28)
- Implementação inicial completa
- Dashboard interativo
- CRUD completo para todas as entidades
- Sistema de relatórios
- APIs REST
- Interface responsiva
- Sistema de backup e exportação
# Sistema de Gerenciamento de Lojas

Sistema completo para gerenciamento de múltiplas lojas com Django, incluindo dashboard administrativo, controle de acesso por loja, e banco de dados individual para cada loja.

## Funcionalidades

### Super Administrador
- Dashboard com estatísticas gerais do sistema
- Cadastro e gerenciamento de lojas
- Controle de status das lojas (ativa, inativa, suspensa)
- Sistema de backup automático
- Logs de acesso e auditoria
- Notificações do sistema

### Administrador de Loja
- Dashboard específico da loja
- Gerenciamento de clientes
- Gerenciamento de produtos
- Controle de estoque
- Relatórios de vendas
- Estatísticas financeiras

## Instalação

### Pré-requisitos
- Python 3.8+
- PostgreSQL 12+
- Redis (opcional, para cache)

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd lojad
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados
Crie um arquivo `.env` na raiz do projeto com as seguintes configurações:

```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
DB_NAME=lojad_main
DB_USER=postgres
DB_PASSWORD=sua-senha-postgres
DB_HOST=localhost
DB_PORT=5432
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

### 5. Configure o PostgreSQL
```sql
-- Conecte-se ao PostgreSQL como superusuário
CREATE DATABASE lojad_main;
CREATE USER postgres WITH PASSWORD 'sua-senha';
GRANT ALL PRIVILEGES ON DATABASE lojad_main TO postgres;
```

### 6. Execute as migrações
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crie um superusuário
```bash
python manage.py createsuperuser
```

### 8. Execute o servidor
```bash
python manage.py runserver
```

## Uso

### Acesso ao Sistema
1. Acesse `http://localhost:8000`
2. Faça login com suas credenciais
3. Se for super usuário, você verá o dashboard administrativo
4. Se for admin de loja, você verá o dashboard da sua loja

### Criando uma Nova Loja (Super Admin)
1. Acesse "Lojas" no menu lateral
2. Clique em "Nova Loja"
3. Preencha os dados da loja
4. O sistema criará automaticamente:
   - Banco de dados individual para a loja
   - Usuário administrador da loja
   - Senha provisória (enviada por email)

### Gerenciando Clientes (Admin de Loja)
1. Acesse "Clientes" no menu lateral
2. Clique em "Novo Cliente" para cadastrar
3. Use os filtros para buscar clientes
4. Edite ou visualize informações dos clientes

### Gerenciando Produtos (Admin de Loja)
1. Acesse "Produtos" no menu lateral
2. Clique em "Novo Produto" para cadastrar
3. Configure preço, estoque e categoria
4. Faça upload de imagens dos produtos

## Comandos de Gerenciamento

### Criar Loja via Linha de Comando
```bash
python manage.py criar_loja --nome "Minha Loja" --cnpj "12.345.678/0001-90" --email "loja@exemplo.com" --telefone "(11) 99999-9999" --endereco "Rua Exemplo, 123" --cidade "São Paulo" --estado "SP" --cep "01234-567"
```

### Backup de Loja
```bash
# Backup de uma loja específica
python manage.py backup_loja --loja-id <uuid-da-loja>

# Backup de todas as lojas
python manage.py backup_loja --todas
```

## Estrutura do Projeto

```
lojad/
├── lojad/                 # Configurações principais
│   ├── settings.py       # Configurações do Django
│   ├── urls.py          # URLs principais
│   └── database_utils.py # Utilitários de banco
├── lojas/               # App de lojas
│   ├── models.py       # Modelos de dados
│   ├── views.py        # Views
│   ├── forms.py        # Formulários
│   └── management/     # Comandos customizados
├── dashboard/          # App de dashboard
├── usuarios/           # App de usuários
├── templates/          # Templates HTML
└── static/            # Arquivos estáticos
```

## Segurança

- Controle de acesso por loja
- Senhas provisórias com expiração
- Logs de auditoria
- Backup automático
- Validação de dados

## Backup e Restauração

O sistema inclui funcionalidades de backup automático:
- Backup diário das lojas
- Armazenamento seguro dos backups
- Restauração rápida em caso de problemas
- Otimização automática dos bancos

## Suporte

Para suporte técnico ou dúvidas sobre o sistema, entre em contato através dos canais oficiais.

## Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para mais detalhes.




# Como Executar o Sistema de Gerenciamento de Lojas

## ⚡ Início Rápido (Recomendado)

### Método 1: Script Automático

```bash
# 1. Navegue até o diretório do projeto
cd /home/felix/Documentos/lojad

# 2. Crie o ambiente virtual
python3 -m venv venv

# 3. Ative o ambiente virtual
source venv/bin/activate

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Configure o arquivo .env
cp env_example.txt .env
# Edite o .env com suas configurações

# 6. Execute o script de inicialização
./iniciar.sh
```

## 🐳 Usando Docker (Mais Fácil)

### Para Desenvolvimento

```bash
# 1. Certifique-se de ter Docker e Docker Compose instalados
docker --version
docker-compose --version

# 2. Inicie os containers
docker-compose -f docker-compose.dev.yml up --build

# 3. Em outro terminal, execute as migrações
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate

# 4. Crie um super usuário
docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser

# 5. Acesse o sistema
# http://localhost:8000
```

### Para Produção

```bash
# 1. Inicie os containers em background
docker-compose up --build -d

# 2. Execute as migrações
docker-compose exec web python manage.py migrate

# 3. Crie um super usuário
docker-compose exec web python manage.py createsuperuser

# 4. Colete os arquivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# 5. Acesse o sistema
# http://localhost (porta 80)
```

## 🔧 Passo a Passo Manual

### 1. Preparar o Ambiente

```bash
# Clone ou navegue até o diretório
cd /home/felix/Documentos/lojad

# Crie o ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Configurar Banco de Dados

#### Opção A: PostgreSQL (Recomendado)

```bash
# Instale o PostgreSQL
sudo apt-get install postgresql postgresql-contrib  # Ubuntu/Debian

# Inicie o serviço
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Acesse o PostgreSQL
sudo -u postgres psql

# No prompt do PostgreSQL:
CREATE DATABASE lojad_main;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE lojad_main TO postgres;
\q
```

#### Opção B: SQLite (Para Testes Rápidos)

No arquivo `settings.py`, altere:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copie o arquivo de exemplo
cp env_example.txt .env

# Edite o arquivo .env
nano .env  # ou vim .env, ou use seu editor preferido
```

Configurações mínimas necessárias:

```env
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
DB_NAME=lojad_main
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

### 5. Executar Migrações

```bash
# Criar as migrações
python manage.py makemigrations

# Aplicar as migrações
python manage.py migrate

# (Opcional) Configurar extensões do PostgreSQL
python manage.py configurar_banco
```

### 6. Criar Super Usuário

```bash
# Método interativo
python manage.py createsuperuser

# OU método com comando customizado
python manage.py criar_superuser \
  --username admin \
  --email admin@example.com \
  --password admin123 \
  --first-name Admin \
  --last-name Sistema
```

### 7. Coletar Arquivos Estáticos

```bash
python manage.py collectstatic --noinput
```

### 8. Iniciar o Servidor

```bash
# Servidor de desenvolvimento
python manage.py runserver

# Servidor em rede local (acessível por outros dispositivos)
python manage.py runserver 0.0.0.0:8000
```

### 9. Acessar o Sistema

- **URL Principal**: http://127.0.0.1:8000
- **Admin Django**: http://127.0.0.1:8000/admin
- **Login**: Use as credenciais do super usuário

## 🎯 Criar Sua Primeira Loja

### Pelo Interface Web

1. Faça login como super admin
2. Clique em "Lojas" no menu lateral
3. Clique em "Nova Loja"
4. Preencha os dados da loja
5. Clique em "Criar Loja"
6. O sistema enviará um email com senha provisória

### Pela Linha de Comando

```bash
python manage.py criar_loja \
  --nome "Minha Primeira Loja" \
  --cnpj "12.345.678/0001-90" \
  --email "loja@exemplo.com" \
  --telefone "(11) 99999-9999" \
  --endereco "Rua Exemplo, 123" \
  --cidade "São Paulo" \
  --estado "SP" \
  --cep "01234-567"
```

## 🔄 Executar Tarefas Assíncronas (Celery)

### Requisitos

```bash
# Instale e inicie o Redis
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### Iniciar Workers

Abra 3 terminais diferentes:

**Terminal 1 - Django**
```bash
python manage.py runserver
```

**Terminal 2 - Celery Worker**
```bash
celery -A lojad worker --loglevel=info
```

**Terminal 3 - Celery Beat (Agendador)**
```bash
celery -A lojad beat --loglevel=info
```

## 🛠️ Comandos Úteis

### Gerenciamento de Dados

```bash
# Ver estatísticas do sistema
python manage.py estatisticas_sistema

# Criar backup de uma loja
python manage.py backup_loja --loja-id <uuid-da-loja>

# Criar backup de todas as lojas
python manage.py backup_loja --todas

# Otimizar sistema
python manage.py otimizar_sistema --todas

# Limpar dados antigos (logs com mais de 90 dias)
python manage.py limpar_sistema --dias 90 --confirmar

# Exportar dados
python manage.py exportar_dados --tipo lojas --arquivo lojas.csv
python manage.py exportar_dados --tipo clientes --loja-id <uuid> --arquivo clientes.csv
python manage.py exportar_dados --tipo produtos --arquivo produtos.csv

# Importar dados
python manage.py importar_dados --arquivo dados.csv --tipo clientes
```

### Gerenciamento Django

```bash
# Criar novas migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar super usuário
python manage.py createsuperuser

# Shell interativo
python manage.py shell

# Coletar arquivos estáticos
python manage.py collectstatic

# Executar testes
python manage.py test

# Verificar problemas no projeto
python manage.py check
```

## 🐛 Solução de Problemas Comuns

### Erro: "No module named 'django'"

```bash
# Certifique-se de que o ambiente virtual está ativado
source venv/bin/activate

# Reinstale as dependências
pip install -r requirements.txt
```

### Erro: "could not connect to server: Connection refused"

```bash
# Verifique se o PostgreSQL está rodando
sudo systemctl status postgresql

# Inicie o PostgreSQL se necessário
sudo systemctl start postgresql

# Verifique as credenciais no arquivo .env
```

### Erro: "Secret key not found"

```bash
# Certifique-se de que o arquivo .env existe e está configurado
cat .env

# Se não existir, copie do exemplo
cp env_example.txt .env

# Edite e configure
nano .env
```

### Erro: "Port already in use"

```bash
# Encontre o processo usando a porta 8000
sudo lsof -i :8000

# Mate o processo (substitua PID pelo número retornado)
kill -9 PID

# Ou use outra porta
python manage.py runserver 8001
```

### Problemas com Migrações

```bash
# Remova migrações antigas (CUIDADO: só em desenvolvimento)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recrie as migrações
python manage.py makemigrations
python manage.py migrate
```

## 📊 Verificar se Está Funcionando

### 1. Acesse o Sistema

Abra o navegador em http://127.0.0.1:8000

### 2. Faça Login

Use as credenciais do super usuário criado

### 3. Explore o Dashboard

- Veja estatísticas
- Crie uma loja de teste
- Adicione clientes e produtos

### 4. Verifique os Logs

```bash
# Logs do Django
tail -f logs/django.log

# Logs do servidor
# Aparecem no terminal onde você executou runserver
```

## 🎓 Próximos Passos

1. ✅ Sistema rodando
2. ✅ Super usuário criado
3. ✅ Primeira loja criada
4. 📝 Configure email para notificações
5. 📝 Configure backups automáticos
6. 📝 Personalize o sistema
7. 📝 Adicione suas lojas reais
8. 📝 Treine sua equipe

## 📞 Precisa de Ajuda?

- Leia a documentação em `README.md`
- Consulte o guia de instalação em `INSTALACAO.md`
- Veja o resumo do projeto em `RESUMO_PROJETO.md`

---

**Boa sorte!** 🚀








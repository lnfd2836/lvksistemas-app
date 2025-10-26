# Correção: Tabela avaliacao_qualidade_perfilusuario Não Existe

## Problema

O sistema está gerando erro no Heroku com a seguinte mensagem:
```
django.db.utils.OperationalError: no such table: avaliacao_qualidade_perfilusuario
```

## Causa

As migrações do app `avaliacao_qualidade` não foram executadas no banco de dados do Heroku.

## Solução

### 1. Correção Temporária (já aplicada)

O arquivo `email_credentials/db_router.py` foi modificado para tratar o erro quando a tabela não existe, evitando que o sistema quebre completamente.

### 2. Executar Migrações no Heroku

Execute os seguintes comandos no Heroku:

```bash
# Opção 1: Executar migrações manualmente
heroku run python manage.py migrate avaliacao_qualidade

# Ou usando o script de correção:
heroku run python fix_avaliacao_qualidade_migrations.py
```

### 3. Verificar se a Tabela Foi Criada

Execute no console do Heroku:

```bash
heroku run python manage.py shell
```

No shell do Django:

```python
from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='avaliacao_qualidade_perfilusuario'")
result = cursor.fetchone()
print("Tabela existe:", result is not None)
```

### 4. Se o Problema Persistir

Se as migrações não executarem, pode haver um problema com o estado das migrações. Execute:

```bash
# Forçar a reaplicação das migrações
heroku run python manage.py migrate avaliacao_qualidade --fake-initial

# Ou recriar as migrações
heroku run python manage.py makemigrations avaliacao_qualidade
heroku run python manage.py migrate avaliacao_qualidade
```

## Verificação Final

Após executar os comandos, verifique se o erro foi resolvido:

```bash
# Ver logs do Heroku
heroku logs --tail

# Testar acesso ao dashboard
curl https://www.lvksistemas.com.br/dashboard/
```

## Arquivos Modificados

1. `email_credentials/db_router.py` - Adicionado tratamento de erro no método `_get_loja_from_request`
2. `fix_avaliacao_qualidade_migrations.py` - Script para corrigir as migrações

## Nota Importante

O código agora trata a ausência da tabela de forma adequada, evitando que o sistema quebre enquanto as migrações são executadas.


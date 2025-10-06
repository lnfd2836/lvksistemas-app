# Correção de Migração - Campos de Senha no Heroku

## Problema Identificado

O erro nos logs do Heroku indica que a coluna `requires_password_change` não existe na base de dados de produção:

```
ERROR Erro durante processo de login: column usuarios_perfilusuario.requires_password_change does not exist
```

## Causa

A migração `0005_add_password_management_fields.py` não foi aplicada no ambiente de produção do Heroku, embora tenha sido aplicada localmente.

## Solução

### 1. Verificar Status Atual

Primeiro, verifique o status das migrações no Heroku:

```bash
heroku run python manage.py check_migrations --app seu-app-name
```

### 2. Aplicar Migrações

Use o comando seguro que criamos:

```bash
heroku run python manage.py apply_password_migrations --app seu-app-name
```

### 3. Verificar Correção

Após aplicar as migrações, verifique se os campos foram criados:

```bash
heroku run python manage.py verify_schema --app usuarios --model PerfilUsuario --app seu-app-name
```

### 4. Testar Funcionalidade

Teste se os campos estão acessíveis:

```bash
heroku run python manage.py shell --app seu-app-name
```

No shell do Django:
```python
from usuarios.models import PerfilUsuario
# Teste se os campos existem
PerfilUsuario.objects.filter(requires_password_change=True).count()
```

## Comandos Criados

### check_migrations.py
- Verifica status das migrações
- Identifica migrações pendentes
- Verifica se colunas específicas existem
- Compatível com PostgreSQL e SQLite

### apply_password_migrations.py
- Aplica migrações de forma segura
- Inclui verificações pré-migração
- Usa transações para segurança
- Verifica sucesso pós-migração

### verify_schema.py
- Compara schema do modelo com base de dados
- Identifica campos faltantes ou extras
- Suporte para verificação detalhada

## Script Automatizado

Execute o script completo:

```bash
./scripts/apply_heroku_migrations.sh
```

(Lembre-se de editar o nome do app no script)

## Monitoramento

Após aplicar a correção, monitore os logs:

```bash
heroku logs --tail --app seu-app-name
```

Procure por:
- ✅ Ausência de erros "column does not exist"
- ✅ Login funcionando normalmente
- ✅ Middleware de senha funcionando

## Prevenção Futura

Para evitar este problema no futuro:

1. **Procfile atualizado**: Certifique-se que o Procfile inclui:
   ```
   release: python manage.py migrate --noinput
   ```

2. **Verificação pré-deploy**: Sempre verifique migrações pendentes antes do deploy:
   ```bash
   heroku run python manage.py showmigrations --app seu-app-name
   ```

3. **Testes de integração**: Inclua testes que verificam a existência dos campos necessários.

## Rollback (Se Necessário)

Se algo der errado, você pode reverter:

```sql
-- Conecte ao banco via heroku pg:psql
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS requires_password_change;
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS provisional_password_created;
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS password_changed_at;
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS password_change_reminders_sent;
```

## Verificação Final

Após a correção, os seguintes endpoints devem funcionar sem erros:
- `/login/` - Login de usuários
- `/dashboard/` - Dashboard principal
- `/dashboard/admin/usuarios/` - Gestão de usuários

Os logs não devem mais mostrar erros relacionados a `requires_password_change`.
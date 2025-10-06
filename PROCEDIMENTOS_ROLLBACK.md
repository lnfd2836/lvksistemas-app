# Procedimentos de Rollback - Migrações de Senha

## ⚠️ ATENÇÃO - PROCEDIMENTOS DE EMERGÊNCIA

Este documento descreve como reverter as migrações de gestão de senha em caso de problemas críticos.

**USE APENAS EM EMERGÊNCIA!**

## Quando Usar Rollback

### Cenários que Justificam Rollback

1. **Aplicação não inicia** após aplicar migrações
2. **Erros críticos** que impedem funcionamento básico
3. **Corrupção de dados** relacionada aos novos campos
4. **Performance severamente degradada** após migração

### Cenários que NÃO Justificam Rollback

1. Erros menores de configuração
2. Problemas de middleware (podem ser desativados temporariamente)
3. Problemas de interface (podem ser corrigidos sem rollback)

## Métodos de Rollback

### Método 1: Rollback via Django (Recomendado)

#### Passo 1: Verificar Estado Atual

```bash
# Local
python manage.py rollback_password_fields --dry-run

# Heroku
heroku run python manage.py rollback_password_fields --dry-run --app seu-app-name
```

#### Passo 2: Criar Backup

```bash
# Heroku
heroku pg:backups:capture --app seu-app-name

# Local (PostgreSQL)
pg_dump nome_da_base > backup_$(date +%Y%m%d_%H%M%S).sql

# Local (SQLite)
cp db.sqlite3 db_backup_$(date +%Y%m%d_%H%M%S).sqlite3
```

#### Passo 3: Executar Rollback

```bash
# Local
python manage.py rollback_password_fields --confirm --backup-first

# Heroku
heroku run python manage.py rollback_password_fields --confirm --app seu-app-name
```

### Método 2: Rollback via Script (Alternativo)

```bash
# Executar script de rollback
./scripts/rollback_password_migrations.sh seu-app-name
```

### Método 3: Rollback Manual (Último Recurso)

#### Para PostgreSQL

```sql
-- Conectar à base de dados
heroku pg:psql --app seu-app-name

-- Remover colunas
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS requires_password_change;
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS provisional_password_created;
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS password_changed_at;
ALTER TABLE usuarios_perfilusuario DROP COLUMN IF EXISTS password_change_reminders_sent;

-- Verificar estrutura da tabela
\d usuarios_perfilusuario;
```

#### Para SQLite

```bash
# SQLite não suporta DROP COLUMN facilmente
# Seria necessário recriar a tabela - não recomendado em produção
```

## Verificação Pós-Rollback

### 1. Verificar Migrações

```bash
python manage.py showmigrations usuarios
```

Deve mostrar:
```
usuarios
 [X] 0001_initial
 [X] 0002_sessaoativa
 [X] 0003_sessaoativa_is_super_admin
 [X] 0004_perfilusuario_deve_trocar_senha_and_more
 [ ] 0005_add_password_management_fields
```

### 2. Testar Acesso ao Modelo

```bash
python manage.py shell
```

```python
from usuarios.models import PerfilUsuario
# Deve funcionar sem erros
count = PerfilUsuario.objects.count()
print(f"Perfis: {count}")

# Estes devem falhar (campos não existem)
try:
    PerfilUsuario.objects.filter(requires_password_change=True).count()
    print("ERRO: Campo ainda existe!")
except:
    print("OK: Campo removido com sucesso")
```

### 3. Verificar Logs

```bash
heroku logs --tail --app seu-app-name
```

Procurar por:
- ✅ Ausência de erros "column does not exist"
- ✅ Aplicação iniciando normalmente
- ✅ Requests sendo processados

## Ações Pós-Rollback

### 1. Desativar Middleware (Temporário)

Editar `settings.py`:

```python
MIDDLEWARE = [
    # ... outros middlewares ...
    # 'usuarios.mandatory_password_middleware.MandatoryPasswordChangeMiddleware',  # Comentar esta linha
]
```

### 2. Atualizar Código

Remover referências aos campos de senha do código:

```python
# usuarios/models.py - Remover estes campos:
# requires_password_change = models.BooleanField(default=False)
# provisional_password_created = models.DateTimeField(null=True, blank=True)
# password_changed_at = models.DateTimeField(null=True, blank=True)
# password_change_reminders_sent = models.IntegerField(default=0)
```

### 3. Testar Funcionalidade Básica

- [ ] Login de utilizadores
- [ ] Criação de utilizadores
- [ ] Acesso ao dashboard
- [ ] Gestão de utilizadores

## Restauração de Backup (Se Necessário)

### Heroku

```bash
# Listar backups disponíveis
heroku pg:backups --app seu-app-name

# Restaurar backup mais recente
heroku pg:backups:restore --app seu-app-name

# Restaurar backup específico
heroku pg:backups:restore b001 --app seu-app-name
```

### Local

```bash
# PostgreSQL
psql nome_da_base < backup_YYYYMMDD_HHMMSS.sql

# SQLite
cp db_backup_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3
```

## Prevenção de Problemas Futuros

### 1. Testes Mais Rigorosos

```bash
# Sempre testar migrações em ambiente de staging primeiro
heroku run python manage.py migrate --dry-run --app staging-app-name
```

### 2. Backups Automáticos

```bash
# Configurar backups automáticos no Heroku
heroku pg:backups:schedule DATABASE_URL --at '02:00 America/Sao_Paulo' --app seu-app-name
```

### 3. Monitoramento Proativo

```bash
# Usar o comando de monitoramento regularmente
heroku run python manage.py monitor_database_health --app seu-app-name
```

## Checklist de Rollback

### Pré-Rollback
- [ ] Problema confirmado como crítico
- [ ] Backup da base de dados criado
- [ ] Equipe notificada
- [ ] Plano de rollback revisado

### Durante Rollback
- [ ] Comando de rollback executado
- [ ] Logs monitorados
- [ ] Verificações pós-rollback executadas
- [ ] Funcionalidade básica testada

### Pós-Rollback
- [ ] Middleware desativado (se necessário)
- [ ] Código atualizado
- [ ] Aplicação testada completamente
- [ ] Equipe notificada do status
- [ ] Plano de correção alternativa preparado

## Comandos de Emergência

```bash
# Verificação rápida de saúde
heroku run python manage.py monitor_database_health --app seu-app-name

# Rollback de emergência
heroku run python manage.py rollback_password_fields --confirm --app seu-app-name

# Reiniciar aplicação
heroku restart --app seu-app-name

# Verificar status
heroku ps --app seu-app-name

# Logs em tempo real
heroku logs --tail --app seu-app-name

# Restaurar backup
heroku pg:backups:restore --app seu-app-name
```

## Contactos de Emergência

- **Administrador de Sistema**: [seu-email]
- **Equipe de Desenvolvimento**: [email-equipe]
- **Suporte Heroku**: https://help.heroku.com

## Notas Importantes

1. **Perda de Dados**: O rollback resultará na perda de todos os dados relacionados à gestão de senhas
2. **Funcionalidade**: A funcionalidade de troca obrigatória de senha ficará indisponível
3. **Middleware**: O middleware de senha deve ser desativado após o rollback
4. **Testes**: Teste completamente a aplicação após o rollback
5. **Plano B**: Tenha sempre um plano alternativo para implementar a funcionalidade
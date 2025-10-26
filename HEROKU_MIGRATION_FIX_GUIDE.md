# Guia de Correção das Migrações do Controle Financeiro no Heroku

## Problema
A tabela `controle_financeiro_controlefinanceiro` não existe no banco de dados do Heroku, causando erros ao acessar funcionalidades do módulo de controle financeiro.

## Soluções (Execute uma das opções abaixo)

### Opção 1: Script Automático (RECOMENDADO)
```bash
heroku run python heroku_migration_fix.py --app seu-app-heroku
```

### Opção 2: Comando Django Personalizado
```bash
heroku run python manage.py fix_heroku_migrations --app seu-app-heroku
```

### Opção 3: Comandos Manuais
```bash
# 1. Executar migrações com fake-initial
heroku run python manage.py migrate controle_financeiro --fake-initial --app seu-app-heroku

# 2. Executar migrações pendentes
heroku run python manage.py migrate controle_financeiro --app seu-app-heroku

# 3. Criar plano padrão
heroku run python manage.py criar_planos_financeiros --app seu-app-heroku
```

### Opção 4: Forçar Criação das Tabelas
```bash
heroku run python force_create_controle_financeiro_tables.py --app seu-app-heroku
```

## Verificação
Após executar qualquer uma das opções, verifique se funcionou:

```bash
# Verificar se as tabelas foram criadas
heroku run python manage.py dbshell --app seu-app-heroku
# No shell do banco: .tables

# Ou verificar via Django
heroku run python manage.py shell --app seu-app-heroku
# No shell Python:
# from controle_financeiro.models import ControleFinanceiro, PlanoFinanceiro
# print(f"Planos: {PlanoFinanceiro.objects.count()}")
# print(f"Controles: {ControleFinanceiro.objects.count()}")
```

## O que cada script faz

### heroku_migration_fix.py
- ✅ Verifica se as tabelas existem
- ✅ Cria tabelas manualmente se necessário
- ✅ Insere dados padrão
- ✅ Marca migrações como aplicadas
- ✅ Verifica se os modelos funcionam

### fix_heroku_migrations (comando Django)
- ✅ Executa migrações normalmente primeiro
- ✅ Se falhar, cria tabelas manualmente
- ✅ Marca migrações como aplicadas
- ✅ Cria dados padrão

### force_create_controle_financeiro_tables.py
- ✅ Força criação de todas as tabelas
- ✅ Insere dados padrão completos
- ✅ Marca todas as migrações como aplicadas

## Tabelas que serão criadas
- `controle_financeiro_planofinanceiro`
- `controle_financeiro_controlefinanceiro`
- `controle_financeiro_cobrancaasaas`
- `controle_financeiro_syncstatus`
- `controle_financeiro_configuracaoboleto`
- `controle_financeiro_boletogerado`
- `controle_financeiro_pagamento`
- `controle_financeiro_notificacaofinanceira`

## Dados padrão criados
- Plano Básico (R$ 29,90/mês, 30 dias trial)
- Status de sincronização inicial
- Configurações básicas do sistema

## Troubleshooting

### Se ainda houver erros após a correção:
```bash
# Verificar logs do Heroku
heroku logs --tail --app seu-app-heroku

# Reiniciar o dyno
heroku restart --app seu-app-heroku

# Verificar variáveis de ambiente
heroku config --app seu-app-heroku
```

### Se as migrações continuarem falhando:
```bash
# Resetar migrações (CUIDADO: pode perder dados)
heroku run python manage.py migrate controle_financeiro zero --app seu-app-heroku
heroku run python manage.py migrate controle_financeiro --app seu-app-heroku
```

## Comandos úteis para debug
```bash
# Ver estado das migrações
heroku run python manage.py showmigrations controle_financeiro --app seu-app-heroku

# Listar tabelas do banco
heroku run python manage.py dbshell --app seu-app-heroku
# No shell: .tables

# Verificar se os modelos funcionam
heroku run python manage.py shell --app seu-app-heroku
```

## Após a correção
1. ✅ O sistema deve funcionar normalmente
2. ✅ As páginas de controle financeiro devem carregar
3. ✅ Será possível criar cobranças via Asaas
4. ✅ O sistema de sincronização deve funcionar

## Contato
Se ainda houver problemas após seguir este guia, verifique:
1. Se o app Heroku está funcionando
2. Se as variáveis de ambiente estão configuradas
3. Se há espaço suficiente no banco de dados
4. Se não há conflitos com outras migrações
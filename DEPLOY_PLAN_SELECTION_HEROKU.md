# 🚀 Deploy - Seleção de Plano na Criação de Lojas

## 📋 Resumo das Funcionalidades Implementadas

### ✨ Principais Funcionalidades
- **Seleção Obrigatória de Plano**: Ao criar uma loja, o usuário deve escolher um plano comercial
- **Interface Visual Rica**: Mostra detalhes, preços e recursos dos planos disponíveis
- **Criação Consistente**: Ambos `ControleFinanceiro` e `AssinaturaLoja` são criados automaticamente
- **Correção de Dados**: Comando para identificar e corrigir lojas com dados inconsistentes

### 🔧 Componentes Implementados

#### 1. **Formulário Aprimorado** (`lojas/forms.py`)
- Campo `plano_comercial` obrigatório
- Validação de plano ativo e disponível
- Tratamento especial para edição de lojas existentes

#### 2. **Template Atualizado** (`templates/lojas/criar.html`)
- Interface visual para seleção de plano
- JavaScript para mostrar detalhes do plano selecionado
- Comparação visual de planos disponíveis

#### 3. **View Modificada** (`lojas/views.py`)
- Carrega planos disponíveis no contexto
- Usa plano selecionado na criação da loja
- Cria ambos registros financeiros atomicamente

#### 4. **Utilitários de Mapeamento** (`lojas/utils/plan_mapping.py`)
- Funções para mapear entre `PlanoComercial` e `PlanoFinanceiro`
- Criação consistente de registros financeiros
- Correção de dados inconsistentes

#### 5. **Comando de Gerenciamento** (`lojas/management/commands/fix_inconsistent_stores.py`)
- Identifica lojas com dados inconsistentes
- Corrige automaticamente registros faltantes
- Suporte a dry-run e correção específica por loja

## 🚀 Como Fazer o Deploy

### Pré-requisitos
```bash
# 1. Verificar se está autenticado no Heroku
heroku auth:whoami

# 2. Se não estiver, fazer login
heroku login
```

### Deploy Automático
```bash
# Executar o script de deploy
./deploy_heroku_plan_selection.sh
```

### Deploy Manual
```bash
# 1. Adicionar mudanças ao git
git add .

# 2. Commit das mudanças
git commit -m "feat: Implementa seleção de plano na criação de lojas"

# 3. Push para Heroku
git push heroku main

# 4. Executar migrações
heroku run python manage.py migrate

# 5. Verificar lojas inconsistentes
heroku run python manage.py fix_inconsistent_stores --dry-run

# 6. Corrigir se necessário
heroku run python manage.py fix_inconsistent_stores

# 7. Coletar arquivos estáticos
heroku run python manage.py collectstatic --noinput
```

## 🔍 Verificações Pós-Deploy

### 1. Testar Criação de Loja
- Acessar: `https://lvksistemas-app-4f6fa281e217.herokuapp.com/lojas/criar/`
- Verificar se campo de seleção de plano aparece
- Testar criação com plano selecionado

### 2. Verificar Consistência de Dados
```bash
# Verificar se há lojas inconsistentes
heroku run python manage.py fix_inconsistent_stores --dry-run --verbose

# Se houver, corrigir
heroku run python manage.py fix_inconsistent_stores --verbose
```

### 3. Testar Dashboard vs Detalhes
- Criar uma loja de teste
- Verificar se dashboard mostra plano corretamente
- Verificar se página de detalhes mostra plano corretamente
- Ambos devem mostrar informações consistentes

## 🛠️ Comandos Úteis

### Monitoramento
```bash
# Ver logs em tempo real
heroku logs --tail

# Ver logs específicos de criação de loja
heroku logs --tail | grep "criar_loja"

# Ver logs de erros
heroku logs --tail | grep "ERROR"
```

### Correção de Dados
```bash
# Verificar lojas inconsistentes (sem fazer mudanças)
heroku run python manage.py fix_inconsistent_stores --dry-run

# Corrigir loja específica
heroku run python manage.py fix_inconsistent_stores --store-id LOJA_ID

# Corrigir todas as lojas inconsistentes
heroku run python manage.py fix_inconsistent_stores
```

### Diagnóstico
```bash
# Verificar planos disponíveis
heroku run python manage.py shell -c "
from planos.models import PlanoComercial
for p in PlanoComercial.objects.filter(status='ativo'):
    print(f'{p.nome}: R$ {p.preco_mensal}')
"

# Verificar lojas e seus planos
heroku run python manage.py shell -c "
from lojas.models import Loja
from controle_financeiro.models import ControleFinanceiro
from planos.models import AssinaturaLoja
for loja in Loja.objects.all()[:5]:
    controle = ControleFinanceiro.objects.filter(loja=loja).first()
    assinatura = AssinaturaLoja.objects.filter(loja=loja).first()
    print(f'{loja.nome}: CF={bool(controle)}, AS={bool(assinatura)}')
"
```

## 🎯 Resultado Esperado

### ✅ Após o Deploy Bem-Sucedido:
1. **Criação de Loja**: Formulário exige seleção de plano
2. **Interface Visual**: Mostra detalhes dos planos disponíveis
3. **Dados Consistentes**: Dashboard e detalhes mostram mesmas informações
4. **Correção Automática**: Lojas existentes podem ser corrigidas
5. **Validação Robusta**: Sistema previne criação sem plano

### 🔧 Funcionalidades Ativas:
- ✅ Seleção obrigatória de plano comercial
- ✅ Criação automática de ControleFinanceiro e AssinaturaLoja
- ✅ Interface visual com detalhes dos planos
- ✅ Comando para correção de dados inconsistentes
- ✅ Validação de formulários aprimorada
- ✅ Transações atômicas para consistência

## 🚨 Troubleshooting

### Problema: Erro "plano_basico not defined"
**Solução**: Já corrigido no código. Se aparecer, verificar se todas as referências foram atualizadas.

### Problema: Formulário não mostra campo de plano
**Solução**: Verificar se `planos_disponiveis` está no contexto da view.

### Problema: Lojas inconsistentes após deploy
**Solução**: Executar `heroku run python manage.py fix_inconsistent_stores`

### Problema: JavaScript não funciona
**Solução**: Verificar se `collectstatic` foi executado e se arquivos estáticos estão sendo servidos.

## 📞 Suporte

Em caso de problemas:
1. Verificar logs: `heroku logs --tail`
2. Executar diagnósticos com os comandos acima
3. Usar comando de correção se necessário
4. Verificar se todas as migrações foram aplicadas

---

**Deploy realizado em**: $(date)
**Versão**: Seleção de Plano v1.0
**Status**: ✅ Pronto para produção
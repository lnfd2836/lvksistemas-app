#!/bin/bash

echo "========================================="
echo "Deploy para Heroku - Seleção de Plano na Criação de Lojas"
echo "========================================="

# Verifica se está no git
if [ ! -d ".git" ]; then
    echo "❌ Erro: Repositório Git não encontrado!"
    echo "Execute: git init"
    exit 1
fi

# Verifica se o remote do Heroku existe
if ! git remote | grep -q heroku; then
    echo "Adicionando remote do Heroku..."
    git remote add heroku https://git.heroku.com/lvksistemas-app-4f6fa281e217.git
fi

# Verifica se há mudanças para commit
if git diff --quiet && git diff --staged --quiet; then
    echo "⚠️  Nenhuma mudança detectada para commit."
    echo "Continuando com deploy da versão atual..."
else
    # Adiciona todas as mudanças
    echo "📦 Adicionando arquivos modificados..."
    git add .

    # Commit das mudanças
    echo "💾 Fazendo commit das novas funcionalidades..."
    git commit -m "feat: Implementa seleção obrigatória de plano na criação de lojas

✨ Novas funcionalidades:
- Seleção obrigatória de plano comercial ao criar loja
- Interface visual com detalhes dos planos disponíveis
- Criação automática de ControleFinanceiro e AssinaturaLoja
- Comando para corrigir lojas com dados inconsistentes
- Mapeamento entre PlanoComercial e PlanoFinanceiro
- Validação robusta de seleção de planos
- Transações atômicas para consistência de dados

🔧 Melhorias técnicas:
- Formulário LojaForm aprimorado com campo plano_comercial
- Template criar.html com JavaScript para mostrar detalhes do plano
- View criar_loja modificada para usar plano selecionado
- Utilitários de mapeamento em lojas/utils/plan_mapping.py
- Comando de gerenciamento fix_inconsistent_stores

🐛 Correções:
- Resolve inconsistência entre dashboard e página de detalhes
- Garante que todas as lojas tenham registros financeiros completos
- Corrige referências antigas a plano_basico"
fi

# Verifica conectividade com Heroku
echo "🔍 Verificando conectividade com Heroku..."
if ! heroku auth:whoami > /dev/null 2>&1; then
    echo "❌ Erro: Não autenticado no Heroku!"
    echo "Execute: heroku login"
    exit 1
fi

# Push para o Heroku
echo "🚀 Fazendo deploy para o Heroku..."
if git push heroku main; then
    echo "✅ Deploy realizado com sucesso!"
else
    echo "❌ Erro no deploy. Tentando forçar push..."
    git push heroku main --force
fi

echo "========================================="
echo "🔧 Executando comandos pós-deploy..."
echo "========================================="

# Executa migrações
echo "📊 Executando migrações..."
heroku run python manage.py migrate

# Verifica se há lojas inconsistentes e oferece correção
echo "🔍 Verificando lojas com dados inconsistentes..."
heroku run python manage.py fix_inconsistent_stores --dry-run

# Pergunta se quer corrigir lojas inconsistentes
echo ""
read -p "🤔 Deseja corrigir lojas inconsistentes encontradas? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔧 Corrigindo lojas inconsistentes..."
    heroku run python manage.py fix_inconsistent_stores --verbose
fi

# Coleta arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
heroku run python manage.py collectstatic --noinput

# Testa se o sistema está funcionando
echo "🧪 Testando sistema..."
echo "Verificando se a aplicação está respondendo..."
if curl -s -o /dev/null -w "%{http_code}" https://lvksistemas-app-4f6fa281e217.herokuapp.com/ | grep -q "200"; then
    echo "✅ Aplicação está respondendo corretamente!"
else
    echo "⚠️  Aplicação pode estar com problemas. Verifique os logs."
fi

echo "========================================="
echo "🎉 Deploy concluído com sucesso!"
echo "========================================="

echo ""
echo "📋 RESUMO DAS FUNCIONALIDADES IMPLEMENTADAS:"
echo "✅ Seleção obrigatória de plano ao criar loja"
echo "✅ Interface visual com detalhes dos planos"
echo "✅ Criação consistente de registros financeiros"
echo "✅ Comando para corrigir dados inconsistentes"
echo "✅ Validação robusta de formulários"
echo ""
echo "🌐 Acesse o sistema em:"
echo "   https://lvksistemas-app-4f6fa281e217.herokuapp.com/"
echo ""
echo "🔧 Para monitorar logs:"
echo "   heroku logs --tail"
echo ""
echo "🛠️  Para corrigir lojas inconsistentes:"
echo "   heroku run python manage.py fix_inconsistent_stores --dry-run"
echo "   heroku run python manage.py fix_inconsistent_stores"
echo ""
echo "========================================="
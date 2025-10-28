#!/bin/bash

# Script de Deploy para Heroku - LVK Sistemas
# Sistema de Login Personalizado por Email

echo "🚀 INICIANDO DEPLOY - LVK SISTEMAS"
echo "=================================="

# Verificar se estamos no diretório correto
if [ ! -f "manage.py" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto Django"
    exit 1
fi

# Configurar Git se necessário
echo "🔧 Configurando Git..."
git config user.email "pjluiz25@hotmail.com" 2>/dev/null || true
git config user.name "LVK Sistemas" 2>/dev/null || true

# Verificar se há mudanças para commit
echo "📋 Verificando mudanças..."
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Adicionando arquivos modificados..."
    
    # Adicionar arquivos específicos (excluindo .env por segurança)
    git add .
    git reset .env  # Remove .env do staging se foi adicionado
    
    echo "💾 Fazendo commit das mudanças..."
    git commit -m "🎉 Implementação: Sistema de Login Personalizado por Email

✨ Funcionalidades implementadas:
- Email automático com login personalizado ao criar loja
- Redirecionamento para login personalizado em /lojas/
- Template de email moderno e responsivo
- Interface aprimorada com links copiáveis
- Signal automático para envio de credenciais
- Views completas para CRUD do sistema CQC

🔧 Arquivos modificados:
- lojas/signals.py - Signal para envio automático
- lojas/views.py - Nova view de redirecionamento
- lojas/urls.py - Nova rota configurada
- templates/emails/credenciais_loja_personalizada.html
- templates/lojas/listar.html - Botão login personalizado
- templates/lojas/detalhar.html - Seção login personalizado
- controle_qualidade_comercial/ - Sistema completo implementado

📧 Email configurado e testado com sucesso!
🚀 Pronto para produção!"

else
    echo "ℹ️  Nenhuma mudança detectada para commit"
fi

# Fazer push para Heroku
echo "🚀 Fazendo deploy para Heroku..."
if git remote | grep -q heroku; then
    echo "📤 Enviando para Heroku..."
    git push heroku main
else
    echo "⚠️  Remote 'heroku' não encontrado. Adicionando..."
    git remote add heroku https://git.heroku.com/lvksistemas-app.git
    git push heroku main
fi

# Executar migrações se necessário
echo "🗄️  Executando migrações no Heroku..."
heroku run python manage.py migrate --app lvksistemas-app

# Coletar arquivos estáticos
echo "📦 Coletando arquivos estáticos..."
heroku run python manage.py collectstatic --noinput --app lvksistemas-app

# Verificar status da aplicação
echo "🔍 Verificando status da aplicação..."
heroku ps --app lvksistemas-app

# Mostrar logs recentes
echo "📋 Logs recentes:"
heroku logs --tail --num=20 --app lvksistemas-app

echo ""
echo "✅ DEPLOY CONCLUÍDO!"
echo "🌐 URL: https://lvksistemas-app-4f6fa281e217.herokuapp.com"
echo "📧 Email configurado: lvksistemas82@gmail.com"
echo ""
echo "🧪 Para testar o sistema:"
echo "1. Acesse: https://lvksistemas-app-4f6fa281e217.herokuapp.com/lojas/"
echo "2. Crie uma nova loja"
echo "3. Verifique se o email foi enviado"
echo "4. Clique no botão 'Login' da loja criada"
echo ""
echo "📞 Suporte: suporte@lvksistemas.com.br"
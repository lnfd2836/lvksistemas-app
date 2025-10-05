#!/bin/bash

echo "🔧 Aplicando correções de debug para URLs..."

# Adicionar arquivos modificados
git add templates/dashboard/usuarios_super_admin_debug.html
git add dashboard/views.py

# Commit das mudanças
git commit -m "Debug: Add debug template for usuarios super admin to isolate URL issues"

echo "🚀 Fazendo deploy para Heroku..."
git push heroku main

echo "✅ Deploy concluído! Teste as páginas:"
echo "   - /lojas/ (deve funcionar agora)"
echo "   - /dashboard/admin/usuarios/ (testando com template debug)"
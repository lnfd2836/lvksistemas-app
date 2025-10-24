#!/usr/bin/env python
"""
Script para fazer deploy da correção do template listar_boletos.html
"""

import subprocess
import sys

def deploy_correcao():
    """Faz deploy da correção do template"""
    
    print("🔧 Fazendo deploy da correção do template listar_boletos.html...")
    
    try:
        # Adicionar arquivos modificados
        subprocess.run(['git', 'add', 'templates/controle_financeiro/listar_boletos.html'], check=True)
        subprocess.run(['git', 'add', 'templates/controle_financeiro/detalhar.html'], check=True)
        subprocess.run(['git', 'add', 'controle_financeiro/views.py'], check=True)
        
        # Commit das mudanças
        subprocess.run([
            'git', 'commit', '-m', 
            'Fix: Corrigir sintaxe do template listar_boletos.html e adicionar integração Asaas nos controles'
        ], check=True)
        
        # Push para Heroku
        subprocess.run(['git', 'push', 'heroku', 'main'], check=True)
        
        print("✅ Deploy realizado com sucesso!")
        print("🌐 Aguarde alguns minutos para as mudanças serem aplicadas")
        print("📋 Correções aplicadas:")
        print("   - Template listar_boletos.html: Sintaxe corrigida")
        print("   - Template detalhar.html: Integração Asaas adicionada")
        print("   - Views.py: Cobranças Asaas incluídas no contexto")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no deploy: {e}")
        return False
    
    return True

if __name__ == '__main__':
    success = deploy_correcao()
    if not success:
        sys.exit(1)
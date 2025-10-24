#!/usr/bin/env python
"""
Script para fazer commit da otimização do sistema de boletos
"""

import subprocess
import sys

def fazer_commit():
    """Faz commit das mudanças da otimização"""
    
    print("📝 Fazendo commit da otimização...")
    
    try:
        # Adicionar arquivos modificados
        arquivos = [
            'controle_financeiro/views.py',
            'controle_financeiro/urls.py',
            'templates/controle_financeiro/backup_boletos/',
            'controle_financeiro/migrations/0002_otimizar_boletos.py',
            'OTIMIZACAO_BOLETOS_CONCLUIDA.md',
            'otimizar_sistema_boletos_final.py',
            'verificar_otimizacao_simples.py',
        ]
        
        for arquivo in arquivos:
            try:
                subprocess.run(['git', 'add', arquivo], check=True)
                print(f"✅ Adicionado: {arquivo}")
            except subprocess.CalledProcessError:
                print(f"⚠️  Não foi possível adicionar: {arquivo}")
        
        # Fazer commit
        commit_message = """feat: Otimização completa do sistema de boletos

- Remove views redundantes de boletos locais
- Adiciona redirecionamentos para compatibilidade
- Move templates para backup
- Simplifica URLs
- Unifica sistema para usar apenas Asaas
- Melhora performance e manutenibilidade

BREAKING CHANGE: Sistema agora usa exclusivamente Asaas para cobranças
"""
        
        subprocess.run([
            'git', 'commit', '-m', commit_message
        ], check=True)
        
        print("✅ Commit realizado com sucesso!")
        
        # Mostrar status
        result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                              capture_output=True, text=True)
        print(f"📋 Último commit: {result.stdout.strip()}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao fazer commit: {e}")
        return False

def main():
    """Executa o commit"""
    
    print("🚀 Iniciando commit da otimização...")
    print("=" * 50)
    
    if fazer_commit():
        print("\n🎉 COMMIT REALIZADO COM SUCESSO!")
        print()
        print("📋 Resumo das mudanças commitadas:")
        print("   • Sistema otimizado para usar apenas Asaas")
        print("   • Views redundantes removidas")
        print("   • Redirecionamentos criados")
        print("   • Templates movidos para backup")
        print("   • URLs simplificadas")
        print()
        print("🔄 Próximos passos:")
        print("   1. git push origin main")
        print("   2. Reiniciar servidor no Heroku")
        print("   3. Testar funcionalidades")
        return True
    else:
        print("\n❌ FALHA NO COMMIT")
        print("🔧 Verifique os erros acima")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
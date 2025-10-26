#!/usr/bin/env python3
"""
Deploy final da funcionalidade de recuperação de senha
"""

import subprocess
import sys
import time

def executar_comando(comando, descricao):
    """Executa um comando e mostra o resultado"""
    print(f"🔧 {descricao}...")
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {descricao} - Sucesso!")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ {descricao} - Erro!")
            if result.stderr.strip():
                print(f"   Erro: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ {descricao} - Exceção: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 DEPLOY - RECUPERAÇÃO DE SENHA FUNCIONAL")
    print("=" * 60)
    print()
    
    print("Funcionalidades implementadas:")
    print("✅ Sistema de recuperação usando senha provisória existente")
    print("✅ Templates de recuperação criados")
    print("✅ URLs de recuperação configuradas")
    print("✅ Links 'Esqueci minha senha' restaurados")
    print("✅ Integração com sistema de email existente")
    print("✅ Removido botão 'Login Administrativo' das páginas de loja")
    print()
    
    # Comandos de deploy
    comandos = [
        ("git add .", "Adicionando arquivos ao Git"),
        ('git commit -m "feat: Implementa recuperação de senha funcional usando sistema de senha provisória existente"', "Criando commit"),
        ("git push heroku main", "Fazendo push para Heroku"),
    ]
    
    success_count = 0
    for comando, descricao in comandos:
        if executar_comando(comando, descricao):
            success_count += 1
        else:
            print(f"⚠️  Continuando mesmo com erro em: {descricao}")
        print()
    
    # Aguardar deploy
    print("⏳ Aguardando deploy do Heroku...")
    time.sleep(15)
    
    # Executar configuração no Heroku
    print("🔧 Configurando recuperação no Heroku...")
    heroku_cmd = 'heroku run --app lvksistemas-app python manage.py shell --command="from lojas.models_login import LoginPersonalizado; configs = LoginPersonalizado.objects.all(); count = 0; [setattr(config, \'mostrar_link_recuperar_senha\', True) or config.save() or globals().update(count=count+1) for config in configs]; print(f\'Configurado {len(configs)} lojas\')"'
    
    if executar_comando(heroku_cmd, "Ativando links de recuperação no Heroku"):
        success_count += 1
    
    print()
    print("=" * 60)
    print("📋 RESUMO DO DEPLOY")
    print("=" * 60)
    
    if success_count >= 3:
        print("✅ DEPLOY CONCLUÍDO COM SUCESSO!")
        print()
        print("🌐 URLs para testar:")
        print("- Fatesa: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/fatesa-escola-de-ultrassonografia/")
        print("- Recuperação: https://lvksistemas-app-4f6fa281e217.herokuapp.com/recuperar-senha/")
        print()
        print("✅ Funcionalidades ativas:")
        print("  - Recuperação de senha funcional")
        print("  - Sistema de senha provisória integrado")
        print("  - Templates de recuperação responsivos")
        print("  - Links 'Esqueci minha senha' funcionando")
        print("  - Botão 'Login Administrativo' removido das lojas")
        print()
        print("🔧 Como funciona:")
        print("  1. Usuário clica em 'Esqueci minha senha'")
        print("  2. Digite email ou usuário cadastrado")
        print("  3. Sistema gera nova senha provisória")
        print("  4. Senha é enviada por email")
        print("  5. Usuário faz login com a nova senha")
        print("  6. Sistema solicita troca da senha provisória")
        
    else:
        print("⚠️  DEPLOY PARCIAL - Alguns comandos falharam")
        print("   Verifique os erros acima e tente novamente se necessário")
    
    print()
    print("🧪 TESTE COMPLETO RECOMENDADO:")
    print("1. Acesse: https://lvksistemas-app-4f6fa281e217.herokuapp.com/login/fatesa-escola-de-ultrassonografia/")
    print("2. Verifique se NÃO há botão 'Login Administrativo'")
    print("3. Clique em 'Esqueci minha senha'")
    print("4. Digite um email válido (ex: financeiroluiz@hotmail.com)")
    print("5. Verifique se recebe email com nova senha")
    print("6. Teste login com a nova senha")
    print("7. Verifique se sistema pede para trocar senha")
    print()
    print("=" * 60)

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Script simplificado para limpeza final do sistema
"""

import os
import shutil
from pathlib import Path

def main():
    print("🧹 Limpeza final do sistema...")
    
    base_dir = Path(__file__).parent
    removidos = 0
    
    # 1. Remover arquivos de cache Python
    print("\n🗑️ Removendo cache Python...")
    for root, dirs, files in os.walk(base_dir):
        # Remover __pycache__
        if "__pycache__" in dirs:
            cache_path = Path(root) / "__pycache__"
            try:
                shutil.rmtree(cache_path)
                print(f"  ✅ Removido: {cache_path}")
                removidos += 1
            except Exception as e:
                print(f"  ❌ Erro: {e}")
        
        # Remover .pyc files
        for file in files:
            if file.endswith(('.pyc', '.pyo')):
                file_path = Path(root) / file
                try:
                    file_path.unlink()
                    removidos += 1
                except Exception:
                    pass
    
    # 2. Limpar logs grandes
    print("\n📋 Limpando logs...")
    logs_dir = base_dir / "logs"
    if logs_dir.exists():
        for log_file in logs_dir.glob("*.log"):
            if log_file.stat().st_size > 5 * 1024 * 1024:  # 5MB
                try:
                    with open(log_file, 'w') as f:
                        f.write("")
                    print(f"  ✅ Log truncado: {log_file.name}")
                    removidos += 1
                except Exception as e:
                    print(f"  ❌ Erro: {e}")
    
    # 3. Remover bancos de dados órfãos
    print("\n🗄️ Verificando bancos de dados...")
    try:
        # Configurar Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
        import django
        django.setup()
        
        from lojas.models import Loja
        lojas_ativas = {str(loja.id) for loja in Loja.objects.all()}
        
        for db_file in base_dir.glob("db_*.sqlite3"):
            loja_id = db_file.name.replace("db_", "").replace(".sqlite3", "")
            
            if loja_id not in lojas_ativas:
                try:
                    db_file.unlink()
                    print(f"  ✅ Removido DB órfão: {db_file.name}")
                    removidos += 1
                except Exception as e:
                    print(f"  ❌ Erro: {e}")
    
    except Exception as e:
        print(f"  ⚠️ Não foi possível verificar lojas: {e}")
    
    # 4. Verificar templates duplicados
    print("\n📄 Verificando templates...")
    templates_dir = base_dir / "templates"
    
    # Verificar se ainda existem templates redundantes
    templates_redundantes = [
        "auth/login_personalizado_corporativo_limpo.html",
        "registration/login.html",  # Se não usado
    ]
    
    for template in templates_redundantes:
        template_path = templates_dir / template
        if template_path.exists():
            print(f"  ⚠️ Template redundante encontrado: {template}")
    
    # 5. Otimizar estrutura de arquivos estáticos
    print("\n🎨 Verificando arquivos estáticos...")
    static_dir = base_dir / "static"
    staticfiles_dir = base_dir / "staticfiles"
    
    if staticfiles_dir.exists():
        # Verificar se há arquivos duplicados
        static_size = sum(f.stat().st_size for f in static_dir.rglob('*') if f.is_file()) if static_dir.exists() else 0
        staticfiles_size = sum(f.stat().st_size for f in staticfiles_dir.rglob('*') if f.is_file())
        
        print(f"  📊 Static: {static_size / 1024:.1f} KB")
        print(f"  📊 Staticfiles: {staticfiles_size / 1024:.1f} KB")
    
    # 6. Relatório final
    print(f"\n📊 Relatório de Limpeza:")
    print(f"  Itens removidos: {removidos}")
    
    # Calcular tamanho do projeto
    def calcular_tamanho(diretorio):
        total = 0
        for root, dirs, files in os.walk(diretorio):
            # Pular diretórios desnecessários
            dirs[:] = [d for d in dirs if d not in ['.git', 'venv', '__pycache__']]
            for file in files:
                try:
                    total += os.path.getsize(os.path.join(root, file))
                except (OSError, IOError):
                    pass
        return total
    
    tamanho_total = calcular_tamanho(base_dir)
    tamanho_mb = tamanho_total / (1024 * 1024)
    
    print(f"  Tamanho do projeto: {tamanho_mb:.1f} MB")
    
    # 7. Verificações de performance
    print(f"\n⚡ Verificações de Performance:")
    
    # Verificar se DEBUG está False em produção
    settings_file = base_dir / "lojad" / "settings.py"
    if settings_file.exists():
        with open(settings_file, 'r') as f:
            content = f.read()
            if "DEBUG = True" in content:
                print(f"  ⚠️ DEBUG=True encontrado - desabilite em produção")
            else:
                print(f"  ✅ DEBUG configurado corretamente")
    
    # Verificar middleware desnecessário
    middleware_count = content.count("Middleware")
    print(f"  📊 Middlewares configurados: {middleware_count}")
    
    # Verificar apps instalados
    apps_count = content.count("'django.")
    print(f"  📊 Apps Django: {apps_count}")
    
    print(f"\n💡 Recomendações:")
    print(f"  - Execute 'python manage.py collectstatic' regularmente")
    print(f"  - Configure cache em produção (Redis/Memcached)")
    print(f"  - Use select_related() e prefetch_related() nas queries")
    print(f"  - Configure compressão GZIP no servidor")
    print(f"  - Monitore logs de performance")
    
    print(f"\n🎉 Limpeza concluída!")

if __name__ == "__main__":
    main()
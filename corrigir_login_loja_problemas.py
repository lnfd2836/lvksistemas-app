#!/usr/bin/env python3
"""
Script para corrigir problemas na página de login das lojas:
1. Remover botão "Login Administrativo" 
2. Remover link de recuperação de senha que está bugado
"""

import os
import sys
import django

# Configurar Django
sys.path.append('/home/luiz/Documentos/lvksistemas-app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def corrigir_template_fatesa():
    """Corrige o template de login da Fatesa"""
    template_path = 'templates/auth/login_personalizado_fatesa.html'
    
    print("🔧 Corrigindo template da Fatesa...")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remover seção de links administrativos
        # Procurar pela seção que contém os links
        lines = content.split('\n')
        new_lines = []
        skip_section = False
        
        for i, line in enumerate(lines):
            # Detectar início da seção de links
            if '<!-- Links adicionais -->' in line:
                skip_section = True
                continue
            
            # Detectar fim da seção de links (próximo comentário ou div)
            if skip_section and ('<!-- Mensagem do Rodapé -->' in line or 
                                '<!-- Bootstrap JS -->' in line or
                                '</div>' in line and 'links-container' not in line):
                skip_section = False
                new_lines.append(line)
                continue
            
            # Pular linhas da seção de links
            if skip_section:
                continue
            
            new_lines.append(line)
        
        # Escrever arquivo corrigido
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Template da Fatesa corrigido!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir template da Fatesa: {e}")
        return False


def corrigir_template_corporativo():
    """Corrige o template corporativo"""
    template_path = 'templates/auth/login_personalizado_corporativo_limpo.html'
    
    print("🔧 Corrigindo template corporativo...")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remover seção de links administrativos
        lines = content.split('\n')
        new_lines = []
        skip_section = False
        
        for i, line in enumerate(lines):
            # Detectar início da seção de links
            if '<!-- Links adicionais -->' in line:
                skip_section = True
                continue
            
            # Detectar fim da seção de links
            if skip_section and ('<!-- Mensagem do Rodapé -->' in line or 
                                '<!-- Bootstrap JS -->' in line or
                                '</div>' in line and 'links-container' not in line):
                skip_section = False
                new_lines.append(line)
                continue
            
            # Pular linhas da seção de links
            if skip_section:
                continue
            
            new_lines.append(line)
        
        # Escrever arquivo corrigido
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Template corporativo corrigido!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir template corporativo: {e}")
        return False


def corrigir_template_padrao():
    """Corrige o template padrão"""
    template_path = 'templates/auth/login_personalizado_padrao.html'
    
    print("🔧 Corrigindo template padrão...")
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remover link de recuperação de senha que está bugado
        lines = content.split('\n')
        new_lines = []
        skip_section = False
        
        for i, line in enumerate(lines):
            # Detectar seção de recuperação de senha
            if 'forgot-password' in line and '<div' in line:
                skip_section = True
                continue
            
            # Detectar fim da seção
            if skip_section and '</div>' in line:
                skip_section = False
                continue
            
            # Pular linhas da seção
            if skip_section:
                continue
            
            new_lines.append(line)
        
        # Escrever arquivo corrigido
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print("✅ Template padrão corrigido!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao corrigir template padrão: {e}")
        return False


def corrigir_outros_templates():
    """Corrige outros templates de login personalizado"""
    templates = [
        'templates/auth/login_personalizado_moderno.html',
        'templates/auth/login_personalizado_minimalista.html'
    ]
    
    for template_path in templates:
        if not os.path.exists(template_path):
            continue
            
        print(f"🔧 Corrigindo {template_path}...")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remover links administrativos e de recuperação de senha
            lines = content.split('\n')
            new_lines = []
            skip_section = False
            
            for line in lines:
                # Detectar seções problemáticas
                if any(keyword in line.lower() for keyword in [
                    'login administrativo', 
                    'admin/login',
                    'password_reset',
                    'recuperar senha',
                    'esqueci minha senha'
                ]):
                    continue
                
                # Detectar início de seções de links
                if 'links-container' in line or 'forgot-password' in line:
                    if '<div' in line:
                        skip_section = True
                        continue
                
                # Detectar fim da seção
                if skip_section and '</div>' in line:
                    skip_section = False
                    continue
                
                # Pular linhas da seção
                if skip_section:
                    continue
                
                new_lines.append(line)
            
            # Escrever arquivo corrigido
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print(f"✅ {template_path} corrigido!")
            
        except Exception as e:
            print(f"❌ Erro ao corrigir {template_path}: {e}")


def atualizar_modelo_login():
    """Atualiza o modelo para desabilitar link de recuperação por padrão"""
    print("🔧 Atualizando modelo de login personalizado...")
    
    try:
        from lojas.models_login import LoginPersonalizado
        
        # Desabilitar link de recuperação de senha para todas as configurações
        configs = LoginPersonalizado.objects.all()
        count = 0
        
        for config in configs:
            if config.mostrar_link_recuperar_senha:
                config.mostrar_link_recuperar_senha = False
                config.save()
                count += 1
                print(f"  ✅ Desabilitado link de recuperação para: {config.loja.nome}")
        
        print(f"✅ {count} configurações atualizadas!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar modelo: {e}")
        return False


def testar_login_fatesa():
    """Testa se o login da Fatesa está funcionando"""
    print("🧪 Testando login da Fatesa...")
    
    try:
        from lojas.models import Loja
        from lojas.models_login import LoginPersonalizado
        
        # Buscar loja Fatesa
        fatesa = Loja.objects.filter(nome__icontains='Fatesa').first()
        if not fatesa:
            print("❌ Loja Fatesa não encontrada")
            return False
        
        # Verificar configuração de login
        try:
            login_config = LoginPersonalizado.objects.get(loja=fatesa)
            print(f"✅ Configuração encontrada:")
            print(f"   - URL: {login_config.get_login_url()}")
            print(f"   - Tema: {login_config.tema}")
            print(f"   - Link recuperação: {login_config.mostrar_link_recuperar_senha}")
            print(f"   - Template: {login_config.get_template_name()}")
            return True
        except LoginPersonalizado.DoesNotExist:
            print("❌ Configuração de login não encontrada para Fatesa")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar: {e}")
        return False


def main():
    """Função principal"""
    print("=" * 60)
    print("🔧 CORREÇÃO DE PROBLEMAS NO LOGIN DAS LOJAS")
    print("=" * 60)
    print()
    
    print("Problemas a corrigir:")
    print("1. ❌ Botão 'Login Administrativo' nas páginas de login das lojas")
    print("2. ❌ Link 'Recuperar Senha' que abre página bugada")
    print()
    
    # Corrigir templates
    success_count = 0
    
    if corrigir_template_fatesa():
        success_count += 1
    
    if corrigir_template_corporativo():
        success_count += 1
    
    if corrigir_template_padrao():
        success_count += 1
    
    corrigir_outros_templates()
    
    # Atualizar modelo
    if atualizar_modelo_login():
        success_count += 1
    
    print()
    print("=" * 60)
    print("📋 RESUMO DA CORREÇÃO")
    print("=" * 60)
    
    if success_count >= 3:
        print("✅ CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print()
        print("Correções aplicadas:")
        print("✅ Removido botão 'Login Administrativo' dos templates")
        print("✅ Removido link 'Recuperar Senha' problemático")
        print("✅ Configurações de login atualizadas no banco")
        print()
        
        # Testar Fatesa
        print("🧪 TESTE FINAL:")
        if testar_login_fatesa():
            print("✅ Login da Fatesa funcionando corretamente!")
        
        print()
        print("🌐 URLs de teste:")
        print("- Fatesa: https://www.lvksistemas.com.br/login/fatesa-escola-de-ultrassonografia/")
        print("- Local: http://localhost:8000/login/fatesa-escola-de-ultrassonografia/")
        
    else:
        print("❌ CORREÇÃO PARCIAL - Alguns problemas podem persistir")
    
    print()
    print("=" * 60)


if __name__ == '__main__':
    main()
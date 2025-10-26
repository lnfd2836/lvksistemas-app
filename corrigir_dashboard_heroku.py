#!/usr/bin/env python3
"""
Script para corrigir problemas específicos do dashboard no Heroku
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from lojas.models import Loja
from lojas.models_login import LoginPersonalizado
from django.contrib.auth.models import User
from dashboard.services.authentication import AuthenticationService
import logging

logger = logging.getLogger(__name__)

def diagnosticar_problema():
    """Diagnostica problemas específicos do Heroku"""
    
    print("🔍 Diagnosticando problemas do dashboard no Heroku...")
    
    # 1. Verificar lojas e seus usuários
    print("\n📊 Verificando lojas e usuários:")
    lojas = Loja.objects.all()
    
    for loja in lojas:
        print(f"\n🏪 Loja: {loja.nome}")
        print(f"   Status: {loja.status}")
        print(f"   Tipo: {loja.tipo_loja.nome if loja.tipo_loja else 'Não definido'}")
        
        # Verificar admin_user
        if loja.admin_user:
            print(f"   Admin: {loja.admin_user.username}")
            print(f"   Admin ativo: {loja.admin_user.is_active}")
            print(f"   É superuser: {loja.admin_user.is_superuser}")
            
            # Testar AuthenticationService
            try:
                user_store = AuthenticationService.get_user_store(loja.admin_user)
                can_access = AuthenticationService.can_access_store_dashboard(loja.admin_user)
                user_type = AuthenticationService.get_user_type(loja.admin_user)
                
                print(f"   Loja detectada pelo AuthService: {user_store.nome if user_store else 'Nenhuma'}")
                print(f"   Pode acessar dashboard: {can_access}")
                print(f"   Tipo de usuário: {user_type}")
                
            except Exception as e:
                print(f"   ❌ Erro no AuthenticationService: {str(e)}")
        else:
            print(f"   ❌ Sem admin_user definido")
        
        # Verificar login personalizado
        try:
            login_config = loja.login_personalizado
            print(f"   Login personalizado: ✅ Ativo ({login_config.tema})")
            print(f"   URL: {login_config.get_login_url()}")
        except LoginPersonalizado.DoesNotExist:
            print(f"   ❌ Login personalizado não configurado")
        except Exception as e:
            print(f"   ❌ Erro no login personalizado: {str(e)}")

def corrigir_dashboard_fatesa():
    """Corrige o problema da função dashboard_fatesa ausente"""
    
    print("\n🔧 Corrigindo problema da função dashboard_fatesa...")
    
    # Verificar se existe loja do tipo controle_qualidade
    lojas_fatesa = Loja.objects.filter(tipo_loja__nome='controle_qualidade')
    
    if lojas_fatesa.exists():
        print(f"   Encontradas {lojas_fatesa.count()} lojas do tipo controle_qualidade")
        
        # Criar função dashboard_fatesa no views.py
        views_path = 'dashboard/views.py'
        
        # Ler o arquivo atual
        with open(views_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Verificar se a função já existe
        if 'def dashboard_fatesa(' not in content:
            print("   Adicionando função dashboard_fatesa...")
            
            # Função dashboard_fatesa
            dashboard_fatesa_function = '''

def dashboard_fatesa(request, loja):
    """Dashboard personalizado para lojas do tipo controle de qualidade (FATESA)"""
    
    try:
        # Verificar se o usuário pode acessar esta loja
        if not AuthenticationService.can_access_store_dashboard(request.user, loja):
            logger.warning(f"Usuário {request.user.username} tentou acessar loja FATESA {loja.nome} sem permissão")
            messages.error(request, 'Você não tem permissão para acessar esta loja.')
            return redirect('login')
        
        # Obter contexto do dashboard
        dashboard_context = AuthenticationService.get_dashboard_context(request.user)
        
        # Estatísticas específicas para controle de qualidade
        context = {
            'loja': loja,
            'is_fatesa': True,
            'page_title': f'Dashboard - {loja.nome}',
            'user_type': dashboard_context['user_type'],
            'can_access_store': dashboard_context['can_access_store'],
        }
        
        # Tentar obter dados específicos do módulo de avaliação de qualidade
        try:
            from avaliacao_qualidade.models import Curso, Professor, Avaliacao
            
            # Estatísticas básicas
            total_cursos = Curso.objects.filter(loja=loja).count()
            total_professores = Professor.objects.filter(loja=loja).count()
            total_avaliacoes = Avaliacao.objects.filter(curso__loja=loja).count()
            
            # Adicionar ao contexto
            context.update({
                'total_cursos': total_cursos,
                'total_professores': total_professores,
                'total_avaliacoes': total_avaliacoes,
                'modulo_ativo': 'avaliacao_qualidade',
            })
            
        except Exception as e:
            logger.warning(f"Erro ao obter dados de avaliação de qualidade para loja {loja.nome}: {str(e)}")
            # Continuar com contexto básico
            context.update({
                'total_cursos': 0,
                'total_professores': 0,
                'total_avaliacoes': 0,
                'modulo_ativo': 'avaliacao_qualidade',
            })
        
        # Usar template específico do FATESA se existir
        template_paths = [
            'avaliacao_qualidade/dashboard_fatesa.html',
            'dashboard/loja_fatesa.html',
            'dashboard/loja.html'  # Fallback
        ]
        
        for template_path in template_paths:
            try:
                return render(request, template_path, context)
            except Exception:
                continue
        
        # Se nenhum template funcionar, usar o padrão
        logger.warning(f"Nenhum template específico encontrado para FATESA, usando template padrão")
        return render(request, 'dashboard/loja.html', context)
                
    except Exception as e:
        logger.error(f"Erro no dashboard FATESA para loja {loja.nome}: {str(e)}")
        messages.error(request, 'Erro interno ao carregar dashboard da loja. Tente novamente.')
        return redirect('login')
'''
            
            # Encontrar onde inserir a função (antes da última linha)
            lines = content.split('\n')
            
            # Inserir antes do final do arquivo
            lines.insert(-1, dashboard_fatesa_function)
            
            # Escrever de volta
            with open(views_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print("   ✅ Função dashboard_fatesa adicionada")
        else:
            print("   ✅ Função dashboard_fatesa já existe")
    else:
        print("   ℹ️ Nenhuma loja do tipo controle_qualidade encontrada")

def corrigir_redirecionamento_login():
    """Corrige problemas de redirecionamento após login personalizado"""
    
    print("\n🔧 Corrigindo redirecionamentos de login...")
    
    # Verificar se todas as lojas têm login personalizado
    lojas_sem_login = []
    
    for loja in Loja.objects.filter(status='ativa'):
        try:
            login_config = loja.login_personalizado
            if not login_config.ativo:
                print(f"   ⚠️ Login personalizado inativo para {loja.nome}")
        except LoginPersonalizado.DoesNotExist:
            lojas_sem_login.append(loja)
    
    if lojas_sem_login:
        print(f"   Criando login personalizado para {len(lojas_sem_login)} lojas...")
        
        from lojas.signals_login import obter_configuracao_por_tipo_loja
        
        for loja in lojas_sem_login:
            try:
                config = obter_configuracao_por_tipo_loja(loja)
                
                LoginPersonalizado.objects.create(
                    loja=loja,
                    titulo=config['titulo'],
                    subtitulo=config['subtitulo'],
                    tema=config['tema'],
                    cor_primaria=config['cor_primaria'],
                    cor_secundaria=config['cor_secundaria'],
                    cor_fundo=config['cor_fundo'],
                    cor_texto=config['cor_texto'],
                    mensagem_boas_vindas=config['mensagem_boas_vindas'],
                    mensagem_rodape=config['mensagem_rodape'],
                    css_personalizado=config['css_personalizado'],
                    mostrar_logo=config['mostrar_logo'],
                    mostrar_nome_loja=config['mostrar_nome_loja'],
                    permitir_lembrar_senha=config['permitir_lembrar_senha'],
                    mostrar_link_recuperar_senha=config['mostrar_link_recuperar_senha'],
                    ativo=True
                )
                
                print(f"   ✅ Login personalizado criado para {loja.nome}")
                
            except Exception as e:
                print(f"   ❌ Erro ao criar login para {loja.nome}: {str(e)}")

def verificar_templates():
    """Verifica se todos os templates necessários existem"""
    
    print("\n🔍 Verificando templates...")
    
    templates_necessarios = [
        'auth/login_personalizado_padrao.html',
        'auth/login_personalizado_moderno.html',
        'auth/login_personalizado_minimalista.html',
        'auth/login_personalizado_corporativo_limpo.html',
        'auth/login_personalizado_fatesa.html',
        'dashboard/loja.html',
        'dashboard/super_admin.html',
    ]
    
    for template in templates_necessarios:
        template_path = f'templates/{template}'
        if os.path.exists(template_path):
            print(f"   ✅ {template}")
        else:
            print(f"   ❌ {template} - AUSENTE")

def main():
    """Função principal"""
    
    print("🚀 Iniciando correção de problemas do Heroku...")
    
    try:
        diagnosticar_problema()
        corrigir_dashboard_fatesa()
        corrigir_redirecionamento_login()
        verificar_templates()
        
        print("\n✅ Correção concluída!")
        print("\n📋 Próximos passos:")
        print("1. Fazer deploy no Heroku")
        print("2. Testar login personalizado")
        print("3. Verificar dashboard das lojas")
        
    except Exception as e:
        print(f"\n❌ Erro durante correção: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
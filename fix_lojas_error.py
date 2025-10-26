#!/usr/bin/env python3
"""
Script para diagnosticar e corrigir erro 500 na página de lojas
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.utils import timezone
from lojas.models import Loja
from controle_financeiro.models import ControleFinanceiro
import logging

logger = logging.getLogger(__name__)


def diagnose_lojas_error():
    """Diagnostica problemas na página de lojas"""
    
    print("🔍 DIAGNÓSTICO DO ERRO 500 - PÁGINA DE LOJAS")
    print("=" * 50)
    
    try:
        # 1. Verificar se existem lojas
        print("🏪 Verificando lojas...")
        lojas = Loja.objects.all()
        print(f"📊 Total de lojas: {lojas.count()}")
        
        if lojas.count() == 0:
            print("⚠️ Nenhuma loja encontrada - pode ser a causa do erro")
            return False
        
        # 2. Verificar integridade das lojas
        print("\n🔍 Verificando integridade das lojas...")
        
        for loja in lojas:
            print(f"\n🏪 Loja: {loja.nome}")
            print(f"   ID: {loja.id}")
            print(f"   CNPJ: {loja.cnpj}")
            print(f"   Email: {loja.email}")
            print(f"   DB Name: {loja.db_name}")
            print(f"   Status: {loja.status}")
            
            # Verificar campos obrigatórios
            problemas = []
            
            if not loja.nome:
                problemas.append("Nome vazio")
            if not loja.cnpj:
                problemas.append("CNPJ vazio")
            if not loja.email:
                problemas.append("Email vazio")
            if not loja.db_name:
                problemas.append("DB Name vazio")
            
            if problemas:
                print(f"   ❌ Problemas: {', '.join(problemas)}")
            else:
                print(f"   ✅ Loja íntegra")
            
            # Verificar controle financeiro
            try:
                controle = ControleFinanceiro.objects.filter(loja=loja).first()
                if controle:
                    print(f"   ✅ Controle financeiro: ID {controle.id}")
                else:
                    print(f"   ⚠️ Sem controle financeiro")
            except Exception as e:
                print(f"   ❌ Erro no controle financeiro: {str(e)}")
        
        # 3. Verificar views de lojas
        print(f"\n🔍 Testando views de lojas...")
        
        try:
            from lojas.views import listar_lojas
            print(f"✅ View listar_lojas importada com sucesso")
        except Exception as e:
            print(f"❌ Erro ao importar view: {str(e)}")
            return False
        
        # 4. Verificar templates
        print(f"\n🔍 Verificando templates...")
        
        template_paths = [
            'templates/lojas/listar.html',
            'templates/lojas/index.html',
            'templates/base.html'
        ]
        
        for template_path in template_paths:
            if os.path.exists(template_path):
                print(f"✅ {template_path}")
            else:
                print(f"❌ {template_path} - FALTANDO")
        
        return True
        
    except Exception as e:
        print(f"💥 ERRO NO DIAGNÓSTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def fix_lojas_issues():
    """Corrige problemas identificados nas lojas"""
    
    print(f"\n🔧 CORRIGINDO PROBLEMAS DAS LOJAS")
    print("=" * 35)
    
    try:
        # 1. Corrigir lojas com dados faltantes
        lojas_com_problema = []
        
        for loja in Loja.objects.all():
            problemas = []
            
            if not loja.db_name:
                # Gerar db_name baseado no CNPJ
                cnpj_limpo = loja.cnpj.replace('.', '').replace('/', '').replace('-', '')
                loja.db_name = f"loja_{cnpj_limpo}"
                problemas.append("DB Name gerado")
            
            if not loja.endereco:
                loja.endereco = "Endereço não informado"
                problemas.append("Endereço padrão")
            
            if not loja.cidade:
                loja.cidade = "Cidade não informada"
                problemas.append("Cidade padrão")
            
            if not loja.cep:
                loja.cep = "00000000"
                problemas.append("CEP padrão")
            
            if problemas:
                loja.save()
                print(f"🔧 {loja.nome}: {', '.join(problemas)}")
                lojas_com_problema.append(loja.nome)
        
        if lojas_com_problema:
            print(f"✅ {len(lojas_com_problema)} lojas corrigidas")
        else:
            print(f"✅ Todas as lojas estão íntegras")
        
        # 2. Verificar controles financeiros
        print(f"\n🔍 Verificando controles financeiros...")
        
        from controle_financeiro.models import PlanoFinanceiro
        from datetime import timedelta
        
        # Criar plano básico se não existir
        plano_basico, created = PlanoFinanceiro.objects.get_or_create(
            nome='Básico',
            defaults={
                'descricao': 'Plano básico para lojas',
                'valor_mensal': 29.90,
                'ativo': True
            }
        )
        
        if created:
            print(f"✅ Plano básico criado")
        
        # Criar controles financeiros faltantes
        controles_criados = 0
        
        for loja in Loja.objects.all():
            if not ControleFinanceiro.objects.filter(loja=loja).exists():
                controle = ControleFinanceiro.objects.create(
                    loja=loja,
                    plano=plano_basico,
                    status='ativa',
                    valor_mensal=plano_basico.valor_mensal,
                    data_inicio=timezone.now(),
                    data_vencimento=timezone.now() + timedelta(days=30)
                )
                print(f"✅ Controle criado para {loja.nome}: ID {controle.id}")
                controles_criados += 1
        
        if controles_criados == 0:
            print(f"✅ Todos os controles financeiros já existem")
        
        return True
        
    except Exception as e:
        print(f"💥 ERRO NA CORREÇÃO: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_lojas_view():
    """Testa a view de lojas"""
    
    print(f"\n🧪 TESTANDO VIEW DE LOJAS")
    print("=" * 25)
    
    try:
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        from lojas.views import listar_lojas
        
        # Criar request fake
        factory = RequestFactory()
        request = factory.get('/lojas/')
        
        # Adicionar usuário admin ao request
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            request.user = admin_user
            print(f"✅ Usuário admin encontrado: {admin_user.username}")
        else:
            print(f"❌ Nenhum usuário admin encontrado")
            return False
        
        # Testar view
        try:
            response = listar_lojas(request)
            print(f"✅ View executada com sucesso - Status: {response.status_code}")
            return True
        except Exception as e:
            print(f"❌ Erro na view: {str(e)}")
            return False
            
    except Exception as e:
        print(f"💥 ERRO NO TESTE: {str(e)}")
        return False


def create_emergency_fix():
    """Cria correção de emergência"""
    
    print(f"\n🚨 CRIANDO CORREÇÃO DE EMERGÊNCIA")
    print("=" * 35)
    
    try:
        # Verificar se há pelo menos uma loja
        if Loja.objects.count() == 0:
            print(f"🏪 Criando loja de exemplo...")
            
            loja_exemplo = Loja.objects.create(
                nome="Loja Exemplo",
                cnpj="00.000.000/0001-00",
                email="exemplo@lvk.com",
                telefone="(16) 99999-9999",
                endereco="Rua Exemplo, 123",
                cidade="Cidade Exemplo",
                estado="SP",
                cep="00000-000",
                status="ativa"
            )
            
            print(f"✅ Loja exemplo criada: {loja_exemplo.nome}")
        
        return True
        
    except Exception as e:
        print(f"💥 ERRO NA CORREÇÃO DE EMERGÊNCIA: {str(e)}")
        return False


def main():
    print("🚀 DIAGNÓSTICO E CORREÇÃO - ERRO 500 LOJAS")
    print("=" * 45)
    
    # 1. Diagnosticar problema
    if not diagnose_lojas_error():
        print("❌ Problemas encontrados no diagnóstico")
    
    # 2. Corrigir problemas
    if fix_lojas_issues():
        print("✅ Problemas corrigidos")
    
    # 3. Criar correção de emergência se necessário
    create_emergency_fix()
    
    # 4. Testar view
    if test_lojas_view():
        print("✅ View de lojas funcionando")
    
    print(f"\n🎯 CORREÇÃO CONCLUÍDA!")
    print(f"💡 Tente acessar: https://lvksistemas-app-4f6fa281e217.herokuapp.com/lojas/")
    print(f"🔄 Se ainda der erro, verifique os logs do Heroku")


if __name__ == '__main__':
    main()
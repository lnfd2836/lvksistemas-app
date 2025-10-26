#!/usr/bin/env python
"""
Script para testar o isolamento de dados por loja
"""
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

import logging
from django.contrib.auth.models import User
from django.db import connections
from lojas.models import Loja
from lojas.services.isolamento_service import IsolamentoService
from lojas.database_router_isolado import LojaContextManager, get_current_loja_id, get_current_loja_db

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_database_isolation():
    """Testa isolamento de banco de dados"""
    print("=== TESTE DE ISOLAMENTO DE BANCO DE DADOS ===")
    
    try:
        # Obter lojas ativas
        lojas = Loja.objects.filter(status='ativa')[:2]
        
        if len(lojas) < 2:
            print("❌ Necessário pelo menos 2 lojas ativas para teste")
            return False
        
        loja1, loja2 = lojas[0], lojas[1]
        
        print(f"Testando com lojas: {loja1.nome} (ID: {loja1.id}) e {loja2.nome} (ID: {loja2.id})")
        
        # Teste 1: Contexto padrão
        print("\n1. Testando contexto padrão:")
        current_loja = get_current_loja_id()
        current_db = get_current_loja_db()
        print(f"   Loja atual: {current_loja}")
        print(f"   Banco atual: {current_db}")
        
        # Teste 2: Contexto da loja 1
        print(f"\n2. Testando contexto da loja {loja1.nome}:")
        with LojaContextManager(str(loja1.id)):
            current_loja = get_current_loja_id()
            current_db = get_current_loja_db()
            print(f"   Loja atual: {current_loja}")
            print(f"   Banco atual: {current_db}")
            
            if current_loja == str(loja1.id) and current_db == f"loja_{loja1.id}":
                print("   ✅ Contexto correto")
            else:
                print("   ❌ Contexto incorreto")
                return False
        
        # Teste 3: Contexto da loja 2
        print(f"\n3. Testando contexto da loja {loja2.nome}:")
        with LojaContextManager(str(loja2.id)):
            current_loja = get_current_loja_id()
            current_db = get_current_loja_db()
            print(f"   Loja atual: {current_loja}")
            print(f"   Banco atual: {current_db}")
            
            if current_loja == str(loja2.id) and current_db == f"loja_{loja2.id}":
                print("   ✅ Contexto correto")
            else:
                print("   ❌ Contexto incorreto")
                return False
        
        # Teste 4: Volta ao contexto padrão
        print("\n4. Testando volta ao contexto padrão:")
        current_loja = get_current_loja_id()
        current_db = get_current_loja_db()
        print(f"   Loja atual: {current_loja}")
        print(f"   Banco atual: {current_db}")
        
        if current_db == 'default':
            print("   ✅ Voltou ao contexto padrão")
        else:
            print("   ❌ Não voltou ao contexto padrão")
            return False
        
        print("\n✅ Teste de isolamento de banco PASSOU")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de isolamento: {str(e)}")
        return False


def test_user_access_validation():
    """Testa validação de acesso por usuário"""
    print("\n=== TESTE DE VALIDAÇÃO DE ACESSO ===")
    
    try:
        # Obter usuários de teste
        super_admin = User.objects.filter(is_superuser=True).first()
        regular_users = User.objects.filter(is_superuser=False)[:2]
        
        if not super_admin:
            print("❌ Necessário pelo menos 1 super admin para teste")
            return False
        
        if len(regular_users) < 1:
            print("❌ Necessário pelo menos 1 usuário regular para teste")
            return False
        
        # Obter lojas
        lojas = Loja.objects.filter(status='ativa')[:2]
        
        if len(lojas) < 2:
            print("❌ Necessário pelo menos 2 lojas para teste")
            return False
        
        loja1, loja2 = lojas[0], lojas[1]
        
        print(f"Testando com usuários: {super_admin.username} (super admin)")
        for user in regular_users:
            print(f"                      {user.username} (regular)")
        
        # Teste 1: Super admin pode acessar qualquer loja
        print(f"\n1. Testando acesso do super admin:")
        for loja in lojas:
            can_access = IsolamentoService.validate_user_loja_access(super_admin, str(loja.id))
            print(f"   Loja {loja.nome}: {'✅' if can_access else '❌'}")
            
            if not can_access:
                print("   ❌ Super admin deveria poder acessar todas as lojas")
                return False
        
        # Teste 2: Usuários regulares só podem acessar sua loja
        print(f"\n2. Testando acesso de usuários regulares:")
        for user in regular_users:
            user_loja = IsolamentoService.get_user_loja_context(user)
            print(f"   Usuário {user.username}:")
            
            if user_loja and not user_loja['is_super_admin']:
                user_loja_id = user_loja['loja_id']
                print(f"     Loja do usuário: {user_loja['loja_nome']} (ID: {user_loja_id})")
                
                # Testar acesso à própria loja
                can_access_own = IsolamentoService.validate_user_loja_access(user, user_loja_id)
                print(f"     Acesso à própria loja: {'✅' if can_access_own else '❌'}")
                
                # Testar acesso a outras lojas
                for loja in lojas:
                    if str(loja.id) != user_loja_id:
                        can_access_other = IsolamentoService.validate_user_loja_access(user, str(loja.id))
                        print(f"     Acesso à loja {loja.nome}: {'❌' if not can_access_other else '✅ (PROBLEMA!)'}")
                        
                        if can_access_other:
                            print(f"     ❌ Usuário não deveria acessar loja {loja.nome}")
                            return False
            else:
                print(f"     Usuário sem loja associada")
        
        print("\n✅ Teste de validação de acesso PASSOU")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de validação: {str(e)}")
        return False


def test_isolation_service():
    """Testa o serviço de isolamento"""
    print("\n=== TESTE DO SERVIÇO DE ISOLAMENTO ===")
    
    try:
        # Teste 1: Status do isolamento
        print("1. Testando status do isolamento:")
        status = IsolamentoService.get_isolation_status()
        
        print(f"   Bancos configurados: {status.get('configured_loja_databases', 0)}")
        print(f"   Lojas ativas: {status.get('active_lojas', 0)}")
        print(f"   Isolamento ativo: {status.get('isolation_active', False)}")
        
        # Teste 2: Contexto de usuários
        print("\n2. Testando contexto de usuários:")
        
        # Super admin
        super_admin = User.objects.filter(is_superuser=True).first()
        if super_admin:
            context = IsolamentoService.get_user_loja_context(super_admin)
            print(f"   Super admin {super_admin.username}:")
            print(f"     É super admin: {context.get('is_super_admin', False) if context else False}")
            print(f"     Loja: {context.get('loja_nome', 'Nenhuma') if context else 'Nenhuma'}")
        
        # Usuários regulares
        regular_users = User.objects.filter(is_superuser=False)[:2]
        for user in regular_users:
            context = IsolamentoService.get_user_loja_context(user)
            print(f"   Usuário {user.username}:")
            if context and not context['is_super_admin']:
                print(f"     Loja: {context['loja_nome']}")
                print(f"     Banco: {context['db_alias']}")
            else:
                print(f"     Sem contexto de loja")
        
        print("\n✅ Teste do serviço de isolamento PASSOU")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste do serviço: {str(e)}")
        return False


def main():
    """Executa todos os testes"""
    print("🔒 INICIANDO TESTES DE ISOLAMENTO POR LOJA")
    print("=" * 50)
    
    tests = [
        test_database_isolation,
        test_user_access_validation,
        test_isolation_service
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Erro no teste: {str(e)}\n")
    
    print("=" * 50)
    print(f"RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM! Isolamento funcionando corretamente.")
        return True
    else:
        print("⚠️  ALGUNS TESTES FALHARAM! Verificar configuração de isolamento.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
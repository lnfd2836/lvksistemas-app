#!/usr/bin/env python
"""
Script para testar se o botão de excluir está aparecendo
"""

import requests
from bs4 import BeautifulSoup

def testar_botao_excluir():
    """Testa se o botão de excluir está presente na página"""
    
    print("🔍 TESTANDO BOTÃO DE EXCLUIR NA PÁGINA")
    print("=" * 60)
    
    url = "https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/asaas/cobrancas/"
    
    try:
        # Fazer requisição para a página
        response = requests.get(url, timeout=10)
        
        if response.status_code == 302:
            print("⚠️  Página redireciona para login")
            print("   Você precisa estar logado para ver os botões")
            return False
        
        if response.status_code != 200:
            print(f"❌ Erro ao acessar página: {response.status_code}")
            return False
        
        # Analisar HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Procurar por botões de excluir
        botoes_excluir = soup.find_all('button', {'title': 'Excluir Cobrança'})
        
        print(f"✅ Página carregada com sucesso")
        print(f"📊 Botões de excluir encontrados: {len(botoes_excluir)}")
        
        if botoes_excluir:
            print("\n🗑️  BOTÕES ENCONTRADOS:")
            for i, botao in enumerate(botoes_excluir, 1):
                print(f"   {i}. {botao}")
            return True
        else:
            print("\n❌ NENHUM BOTÃO ENCONTRADO!")
            
            # Verificar se há tabela
            tabela = soup.find('table')
            if tabela:
                print("✅ Tabela encontrada")
                
                # Verificar se há cobranças
                linhas = tabela.find_all('tr')
                print(f"📊 Linhas na tabela: {len(linhas)}")
                
                # Procurar por qualquer botão na tabela
                botoes = tabela.find_all('button')
                print(f"🔘 Botões na tabela: {len(botoes)}")
                
                if botoes:
                    print("   Botões encontrados:")
                    for botao in botoes:
                        title = botao.get('title', 'Sem título')
                        classe = botao.get('class', [])
                        print(f"   - {title} (classes: {classe})")
            else:
                print("❌ Nenhuma tabela encontrada")
            
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar: {e}")
        return False

def main():
    """Executa teste"""
    
    print("🚀 DIAGNÓSTICO DO BOTÃO DE EXCLUIR")
    print("=" * 60)
    print("Testando se o botão está aparecendo na página...")
    print()
    
    if testar_botao_excluir():
        print("\n✅ BOTÃO ENCONTRADO!")
        print("Se você não está vendo, pode ser:")
        print("1. Cache do navegador")
        print("2. JavaScript não carregou")
        print("3. CSS ocultando o botão")
        print("4. Problema de responsividade")
    else:
        print("\n❌ BOTÃO NÃO ENCONTRADO!")
        print("Possíveis causas:")
        print("1. Você não está logado")
        print("2. Não há cobranças na página")
        print("3. Erro no template")
        print("4. Problema no deploy")

if __name__ == '__main__':
    main()
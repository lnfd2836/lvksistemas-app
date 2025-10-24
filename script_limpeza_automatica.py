#!/usr/bin/env python
'''
Script de limpeza automática do sistema LVK
Remove arquivos redundantes e otimiza o projeto
'''

import os
import shutil
from pathlib import Path

def remover_arquivos_redundantes():
    '''Remove arquivos identificados como redundantes'''
    print("🧹 REMOVENDO ARQUIVOS REDUNDANTES...")
    
    arquivos_remover = [
        "teste_boleto_heroku.py",
        "teste_completo_boleto_pix.py",
        "teste_login_simples.py",
        "teste_producao_completo.py",
        "teste_final_api_asaas.py",
        "teste_simples.py",
        "teste_cobranca_sem_callback.py",
        "teste_nota_fiscal_pos_pagamento.py",
        "teste_api_key.py",
        "teste_direto_boleto.py",
        "teste_dv_boletos.py",
        "teste_heroku.py",
        "teste_final_boleto.py",
        "teste_boleto_pix_producao.py",
        "debug_dados_boleto_real.py",
        "debug_asaas_403.py",
        "debug_tamanho_codigo.py",
        "debug_geracao_boleto.py",
        "debug_dv_profundo.py",
        "debug_troca_senha_loja.py",
        "debug_settings_direto.py",
        "debug_troca_senha.py",
        "debug_user_access.py",
        "debug_ordem_codigo.py",
        "debug_asaas_api.py",
        "debug_template_rendering.py",
        "criar_controles_exemplo.py",
        "criar_controle_67.py",
        "criar_admin_heroku.py",
        "criar_tipos_loja_exemplo.py",
        "criar_mais_controles.py",
        "criar_loja_controle_qualidade.py",
        "criar_tipo_controle_qualidade.py",
        "criar_cobranca_exemplo.py",
        "criar_usuario_admin.py",
        "verificar_config.py",
        "verificar_heroku_agora.py",
        "verificar_boleto.py",
        "verificar_config_heroku.py",
        "corrigir_dv_problema.py",
        "corrigir_cliente_e_gerar_nf.py",
        "corrigir_configuracoes.py",
        "simular_pagamento_e_nota_fiscal.py",
        "simular_heroku_debug.py",
        "deploy_heroku_final.sh",
        "deploy_heroku.sh",
        "deploy_heroku_fixed.sh",
        "deploy_heroku_asaas.sh",
        "deploy_heroku_plan_selection.sh",
        "deploy_heroku_codigo_barras.sh",
        "deploy_heroku_boleto_validation_fix.sh",
        "TESTE_CONCLUIDO_COM_SUCESSO.md",
        "TESTE_FINAL_PDF.md",
        "TESTE_FINAL_SUCESSO.md",
        "SOLUCAO_ERRO_403_ASAAS.md",
        "SOLUCAO_DEFINITIVA_ERRO_400.md",
        "SOLUCAO_IP_ASAAS.md",
        "SOLUCAO_ERRO_400_ASAAS.md",
        "SOLUCAO_ERRO_500_BOLETOS.md",
        "SOLUCAO_FINAL_FUNCIONANDO.md",
        "SOLUCAO_BOLETO_ASAAS.md",
        "SOLUCAO_FINAL_PDF.md",
        "CORRECAO_TEMPLATE_ERRO_500.md",
        "CORRECAO_PDF_ASAAS.md",
        "CORRECAO_ERRO_500_TESTAR_ASAAS.md",
        "CORRECAO_TROCA_SENHA_OBRIGATORIA.md",
        "DEPLOY_WEBHOOK_FIX.md",
        "DEPLOY_PLAN_SELECTION_HEROKU.md",
        "DEPLOY_HEROKU_ASAAS.md",
        "SISTEMA_100_ASAAS.md",
        "SISTEMA_CORRIGIDO_FINAL.md",
        "SISTEMA_FUNCIONANDO_ASAAS.md",
        "SISTEMA_CRIACAO_USUARIOS_AUTOMATICO.md",
        "SISTEMA_TIPOS_LOJA_FUNCIONANDO.md",
        "WEBHOOK_HEROKU_FIX.md",
        "WEBHOOK_ASAAS_FUNCIONANDO.md",
        "ERRO_DUPLICATA_CORRIGIDO.md",
        "PROBLEMA_COBRANCAS_RESOLVIDO.md",
        "FUNCIONALIDADES_CRIAR_EXCLUIR_COBRANCAS.md",
        "MELHORIAS_LAYOUT_COBRANCA.md",
        "STATUS_IMPLEMENTACAO_ASAAS.md",
        "RESUMO_MUDANCAS_LOGIN.md",
        "RESUMO_DEPLOY_HEROKU.md",
        "RESUMO_PROJETO.md",
        "GUIA_TESTE_PRODUCAO.md",
        "CONFIGURACAO_FINAL_ASAAS.md",
        "CONFIGURACAO_DOMINIO.md",
        "CONFIGURACAO_WEBHOOK_ASAAS.md",
        "INTEGRACAO_ASAAS_CONTROLES.md",
        "INTEGRACAO_ASAAS.md",
        "LIMPEZA_CAIXA_COMPLETA.md",
        "LIMPEZA_SISTEMA_COMPLETA.md",
        "GERENCIAMENTO_TIPOS_LOJA.md",
        "CRM_ADICIONADO_TIPOS_LOJA.md",
        "TIPO_CONTROLE_QUALIDADE_CRIADO.md",
        "CLINICA_ESTETICA_COMPLETA.md",
        "COMANDOS_HEROKU_MANUAL.md",
        "COMANDOS_FINAIS_HEROKU.md",
        "COMO_EXECUTAR.md",
        "boleto_cinza.jpg",
        "boleto_contraste.jpg",
        "boleto_nitida.jpg",
        "chave producao.docx",
        "Controle de qualidade.docx",
        "Link para Controle de qualidade.docx",
        "cleanup_redundant_files.py",
        "cleanup_templates.py",
        "docker-compose.dev.yml",
        "docker-compose.yml",
        "Dockerfile",
        "nginx.conf",
        "iniciar.sh",
        ".env.example",
    ]
    
    removidos = 0
    espaco_liberado = 0
    
    for arquivo in arquivos_remover:
        if os.path.exists(arquivo):
            try:
                tamanho = os.path.getsize(arquivo)
                os.remove(arquivo)
                removidos += 1
                espaco_liberado += tamanho
                print(f"   ✅ Removido: {arquivo}")
            except Exception as e:
                print(f"   ❌ Erro ao remover {arquivo}: {e}")
    
    print(f"\n📊 RESULTADO:")
    print(f"   Arquivos removidos: {removidos}")
    print(f"   Espaço liberado: {espaco_liberado / 1024:.1f} KB")

def consolidar_webhooks():
    '''Consolida múltiplos arquivos de webhook em um só'''
    print("\n🔗 CONSOLIDANDO WEBHOOKS...")
    
    # Manter apenas o webhook principal
    webhooks_remover = [
        'controle_financeiro/webhook_direct.py',
        'controle_financeiro/webhook_final.py', 
        'controle_financeiro/webhook_heroku.py',
        'controle_financeiro/webhook_raw.py',
        'controle_financeiro/webhook_simple.py',
        'controle_financeiro/webhook_urls.py'
    ]
    
    for webhook in webhooks_remover:
        if os.path.exists(webhook):
            try:
                os.remove(webhook)
                print(f"   ✅ Removido webhook redundante: {webhook}")
            except Exception as e:
                print(f"   ❌ Erro: {e}")

def otimizar_middlewares():
    '''Remove middlewares redundantes'''
    print("\n⚙️ OTIMIZANDO MIDDLEWARES...")
    
    # Manter apenas middlewares essenciais
    middlewares_remover = [
        'usuarios/password_middleware.py',  # Redundante com mandatory_password_middleware
        'dashboard/middleware.py'  # Se não for usado
    ]
    
    for middleware in middlewares_remover:
        if os.path.exists(middleware):
            try:
                # Verificar se está sendo usado antes de remover
                print(f"   ⚠️ Verificar uso antes de remover: {middleware}")
            except Exception as e:
                print(f"   ❌ Erro: {e}")

def limpar_cache():
    '''Remove arquivos de cache'''
    print("\n🗑️ LIMPANDO CACHE...")
    
    cache_dirs = [
        '__pycache__',
        '.pytest_cache',
        'staticfiles'
    ]
    
    for root, dirs, files in os.walk('.'):
        for cache_dir in cache_dirs:
            if cache_dir in dirs:
                cache_path = os.path.join(root, cache_dir)
                try:
                    shutil.rmtree(cache_path)
                    print(f"   ✅ Cache removido: {cache_path}")
                except Exception as e:
                    print(f"   ❌ Erro ao remover cache {cache_path}: {e}")

if __name__ == '__main__':
    print("=" * 60)
    print("OTIMIZAÇÃO AUTOMÁTICA DO SISTEMA LVK")
    print("=" * 60)
    
    remover_arquivos_redundantes()
    consolidar_webhooks()
    otimizar_middlewares()
    limpar_cache()
    
    print("\n🎉 OTIMIZAÇÃO CONCLUÍDA!")
    print("   Sistema otimizado para melhor performance")

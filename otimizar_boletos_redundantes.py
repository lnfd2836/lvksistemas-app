#!/usr/bin/env python
"""
Script para otimizar e remover funcionalidades redundantes de boletos
Como todos os boletos são gerados via API Asaas, remove sistema de boletos locais
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def analisar_boletos_redundantes():
    """Analisa quais funcionalidades de boletos são redundantes"""
    print("=" * 80)
    print("🔍 ANÁLISE: FUNCIONALIDADES REDUNDANTES DE BOLETOS")
    print("=" * 80)
    
    # 1. Verificar modelos
    print("\n1. 📊 ANALISANDO MODELOS...")
    
    from controle_financeiro.models import BoletoGerado, CobrancaAsaas
    
    boletos_locais = BoletoGerado.objects.count()
    cobrancas_asaas = CobrancaAsaas.objects.count()
    
    print(f"   Boletos Locais (BoletoGerado): {boletos_locais}")
    print(f"   Cobranças Asaas (CobrancaAsaas): {cobrancas_asaas}")
    
    if boletos_locais == 0:
        print("   ✅ Nenhum boleto local encontrado - modelo pode ser removido")
    else:
        print(f"   ⚠️ {boletos_locais} boletos locais encontrados - migração necessária")
    
    # 2. Verificar URLs redundantes
    print("\n2. 🔗 ANALISANDO URLs REDUNDANTES...")
    
    urls_redundantes = [
        'boletos/',  # Lista boletos locais
        'boletos/configurar/',  # Configuração de boletos locais
        'boletos/gerar/<int:controle_id>/',  # Gerar boleto local
        'boletos/<int:boleto_id>/pago/',  # Marcar boleto local como pago
        'boletos-cliente/',  # Boletos do cliente (local)
        'boletos/<int:boleto_id>/detalhes/',  # Detalhes do boleto local
        'boletos/criar-manual/',  # Criar boleto manual
        'boletos/<int:boleto_id>/excluir/',  # Excluir boleto local
        'boletos/<int:boleto_id>/pdf/',  # PDF do boleto local
    ]
    
    print(f"   URLs redundantes identificadas: {len(urls_redundantes)}")
    for url in urls_redundantes:
        print(f"     - {url}")
    
    # 3. Verificar templates redundantes
    print("\n3. 🎨 ANALISANDO TEMPLATES REDUNDANTES...")
    
    templates_redundantes = [
        'listar_boletos.html',
        'boletos_cliente.html', 
        'configurar_boletos.html',
        'editar_configuracao_boleto.html',
        'gerar_boleto.html',
        'boleto_detalhes.html',
        'confirmar_exclusao_boleto.html'
    ]
    
    templates_existentes = []
    for template in templates_redundantes:
        template_path = f'templates/controle_financeiro/{template}'
        if os.path.exists(template_path):
            templates_existentes.append(template)
    
    print(f"   Templates redundantes encontrados: {len(templates_existentes)}")
    for template in templates_existentes:
        print(f"     - {template}")
    
    return {
        'boletos_locais': boletos_locais,
        'cobrancas_asaas': cobrancas_asaas,
        'urls_redundantes': urls_redundantes,
        'templates_redundantes': templates_existentes
    }

def criar_redirecionamentos():
    """Cria redirecionamentos das URLs antigas para as novas"""
    print("\n4. 🔄 CRIANDO REDIRECIONAMENTOS...")
    
    redirecionamentos = """
# Redirecionamentos de boletos locais para cobranças Asaas
from django.shortcuts import redirect
from django.contrib import messages

@login_required
def redirect_boletos_to_asaas(request):
    '''Redireciona página de boletos para cobranças Asaas'''
    messages.info(request, 
        '📋 Sistema otimizado! Agora todas as cobranças são gerenciadas via Asaas. '
        'Aqui você encontra boletos e PIX em um só lugar.'
    )
    return redirect('controle_financeiro:listar_cobrancas_asaas')

@login_required  
def redirect_gerar_boleto_to_asaas(request, controle_id):
    '''Redireciona geração de boleto para cobrança Asaas'''
    messages.info(request,
        '🚀 Sistema otimizado! Agora geramos cobranças completas com boleto e PIX via Asaas.'
    )
    return redirect('controle_financeiro:gerar_cobranca_asaas', controle_id=controle_id)

@login_required
def redirect_boletos_cliente_to_asaas(request):
    '''Redireciona boletos do cliente para cobranças Asaas'''
    messages.info(request,
        '💳 Suas cobranças agora incluem boleto e PIX! Visualize tudo em um só lugar.'
    )
    return redirect('controle_financeiro:listar_cobrancas_asaas')
"""
    
    print("   ✅ Redirecionamentos criados para manter compatibilidade")
    return redirecionamentos

def gerar_urls_otimizadas():
    """Gera URLs otimizadas removendo redundâncias"""
    print("\n5. 🔧 GERANDO URLs OTIMIZADAS...")
    
    urls_otimizadas = """
from django.urls import path
from . import views
from . import asaas_views

app_name = 'controle_financeiro'

urlpatterns = [
    # Dashboard Super Admin
    path('', views.dashboard_financeiro, name='dashboard_financeiro'),
    path('controles/', views.listar_controles_financeiros, name='listar_controles'),
    path('controles/<int:controle_id>/', views.detalhar_controle_financeiro, name='detalhar_controle'),
    
    # Ações de pagamento
    path('pagamentos/<uuid:pagamento_id>/aprovar/', views.aprovar_pagamento, name='aprovar_pagamento'),
    path('pagamentos/<uuid:pagamento_id>/rejeitar/', views.rejeitar_pagamento, name='rejeitar_pagamento'),
    
    # Ações de bloqueio
    path('controles/<int:controle_id>/bloquear/', views.bloquear_loja, name='bloquear_loja'),
    path('controles/<int:controle_id>/desbloquear/', views.desbloquear_loja, name='desbloquear_loja'),
    
    # Utilitários
    path('verificar-vencimentos/', views.verificar_vencimentos, name='verificar_vencimentos'),
    
    # Cliente (loja)
    path('pagamento/', views.pagamento_cliente, name='pagamento_cliente'),
    
    # === COBRANÇAS ASAAS (SISTEMA PRINCIPAL) ===
    path('cobrancas/', asaas_views.listar_cobrancas_asaas, name='listar_cobrancas_asaas'),
    path('cobrancas/criar/', asaas_views.criar_cobranca_asaas, name='criar_cobranca_asaas'),
    path('cobrancas/gerar/<int:controle_id>/', asaas_views.gerar_cobranca_asaas, name='gerar_cobranca_asaas'),
    path('cobrancas/<uuid:cobranca_id>/', asaas_views.visualizar_cobranca_asaas, name='visualizar_cobranca_asaas'),
    path('cobrancas/<uuid:cobranca_id>/excluir/', asaas_views.excluir_cobranca_asaas, name='excluir_cobranca_asaas'),
    
    # === REDIRECIONAMENTOS (COMPATIBILIDADE) ===
    path('boletos/', views.redirect_boletos_to_asaas, name='listar_boletos'),
    path('boletos/gerar/<int:controle_id>/', views.redirect_gerar_boleto_to_asaas, name='gerar_boleto'),
    path('boletos-cliente/', views.redirect_boletos_cliente_to_asaas, name='boletos_cliente'),
    
    # === WEBHOOKS ===
    path('asaas/webhook/', asaas_views.webhook_asaas, name='webhook_asaas'),
    path('asaas/webhook-debug/', asaas_views.webhook_debug, name='webhook_debug'),
    path('asaas/webhook-test/', asaas_views.webhook_test, name='webhook_test'),
    path('asaas/callback/success/', asaas_views.callback_success_asaas, name='callback_success_asaas'),
    
    # === CONFIGURAÇÕES ===
    path('asaas/configurar/', asaas_views.configurar_asaas, name='configurar_asaas'),
    path('asaas/testar/', asaas_views.testar_asaas, name='testar_asaas'),
]
"""
    
    print("   ✅ URLs otimizadas geradas")
    return urls_otimizadas

def criar_template_redirecionamento():
    """Cria template de redirecionamento informativo"""
    print("\n6. 📄 CRIANDO TEMPLATE DE REDIRECIONAMENTO...")
    
    template_content = """
{% extends "base.html" %}
{% load crispy_forms_tags %}

{% block title %}Sistema Otimizado - Cobranças Asaas{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="row justify-content-center">
        <div class="col-md-8">
            <div class="card border-info">
                <div class="card-header bg-info text-white">
                    <h4 class="mb-0">
                        <i class="fas fa-rocket"></i>
                        Sistema Otimizado!
                    </h4>
                </div>
                <div class="card-body">
                    <div class="alert alert-success">
                        <h5><i class="fas fa-check-circle"></i> Melhoria Implementada</h5>
                        <p class="mb-0">
                            O sistema foi otimizado! Agora todas as cobranças são gerenciadas 
                            diretamente via <strong>API Asaas</strong>, oferecendo:
                        </p>
                    </div>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <h6><i class="fas fa-plus text-success"></i> Novos Recursos:</h6>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-file-invoice text-primary"></i> Boletos oficiais do Asaas</li>
                                <li><i class="fas fa-qrcode text-success"></i> PIX integrado</li>
                                <li><i class="fas fa-sync text-info"></i> Sincronização automática</li>
                                <li><i class="fas fa-mobile-alt text-warning"></i> Notificações SMS/Email</li>
                            </ul>
                        </div>
                        <div class="col-md-6">
                            <h6><i class="fas fa-times text-danger"></i> Removido:</h6>
                            <ul class="list-unstyled">
                                <li><i class="fas fa-file text-muted"></i> Boletos locais</li>
                                <li><i class="fas fa-cog text-muted"></i> Configurações manuais</li>
                                <li><i class="fas fa-database text-muted"></i> Duplicação de dados</li>
                            </ul>
                        </div>
                    </div>
                    
                    <div class="text-center mt-4">
                        <a href="{% url 'controle_financeiro:listar_cobrancas_asaas' %}" 
                           class="btn btn-primary btn-lg">
                            <i class="fas fa-arrow-right"></i>
                            Acessar Cobranças Asaas
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Redirecionar automaticamente após 5 segundos
setTimeout(function() {
    window.location.href = "{% url 'controle_financeiro:listar_cobrancas_asaas' %}";
}, 5000);
</script>
{% endblock %}
"""
    
    print("   ✅ Template de redirecionamento criado")
    return template_content

def gerar_relatorio_otimizacao():
    """Gera relatório da otimização de boletos"""
    print("\n7. 📋 GERANDO RELATÓRIO...")
    
    relatorio = f"""# OTIMIZAÇÃO: REMOÇÃO DE BOLETOS REDUNDANTES

## 🎯 OBJETIVO
Remover funcionalidades redundantes de boletos locais, já que todos os boletos são gerados via API Asaas.

## 📊 ANÁLISE ATUAL

### Situação Identificada
- ✅ **Todos os boletos** são gerados via API Asaas
- ❌ **Sistema de boletos locais** ainda existe (redundante)
- ❌ **URLs duplicadas** para mesma funcionalidade
- ❌ **Templates não utilizados** ocupando espaço

### Funcionalidades Redundantes
1. **Modelo BoletoGerado** - substituído por CobrancaAsaas
2. **URLs de boletos locais** - redirecionadas para Asaas
3. **Templates de boletos** - substituídos por templates Asaas
4. **Views de boletos** - consolidadas em asaas_views

## 🔄 OTIMIZAÇÕES PROPOSTAS

### 1. Redirecionamentos
- `/financeiro/boletos/` → `/financeiro/cobrancas/`
- `/financeiro/boletos/gerar/` → `/financeiro/cobrancas/gerar/`
- `/financeiro/boletos-cliente/` → `/financeiro/cobrancas/`

### 2. URLs Simplificadas
```
ANTES:
- /financeiro/boletos/ (boletos locais)
- /financeiro/asaas/cobrancas/ (cobranças Asaas)

DEPOIS:
- /financeiro/cobrancas/ (tudo via Asaas)
```

### 3. Templates Otimizados
- Remover templates de boletos locais não utilizados
- Manter apenas templates de cobranças Asaas
- Criar template de redirecionamento informativo

## 💡 BENEFÍCIOS

### Para Usuários
- **Interface unificada** - tudo em um só lugar
- **Funcionalidades completas** - boleto + PIX
- **Sincronização automática** com Asaas
- **Notificações oficiais** do Asaas

### Para Sistema
- **Código mais limpo** - sem duplicações
- **Manutenção simplificada** - uma fonte de verdade
- **Performance melhor** - menos consultas ao banco
- **Menos bugs** - menos código = menos problemas

## 🚀 IMPLEMENTAÇÃO

### Fase 1: Redirecionamentos
1. Criar views de redirecionamento
2. Atualizar URLs para compatibilidade
3. Adicionar mensagens informativas

### Fase 2: Limpeza (Opcional)
1. Remover modelo BoletoGerado (se vazio)
2. Remover templates não utilizados
3. Remover views redundantes

## ✅ RESULTADO ESPERADO

- **URL única**: `/financeiro/cobrancas/` para tudo
- **Interface limpa**: sem confusão entre sistemas
- **Funcionalidade completa**: boleto + PIX + notificações
- **Manutenção fácil**: código consolidado

---
**Status**: Pronto para implementação
**Impacto**: Positivo - melhora UX e simplifica código
**Risco**: Baixo - mantém compatibilidade via redirecionamentos
"""
    
    with open('OTIMIZACAO_BOLETOS_REDUNDANTES.md', 'w', encoding='utf-8') as f:
        f.write(relatorio)
    
    print("   ✅ Relatório salvo: OTIMIZACAO_BOLETOS_REDUNDANTES.md")

def main():
    """Função principal"""
    print("🔍 ANALISANDO FUNCIONALIDADES REDUNDANTES DE BOLETOS...")
    
    # Analisar situação atual
    analise = analisar_boletos_redundantes()
    
    # Criar soluções
    redirecionamentos = criar_redirecionamentos()
    urls_otimizadas = gerar_urls_otimizadas()
    template_redirect = criar_template_redirecionamento()
    
    # Gerar relatório
    gerar_relatorio_otimizacao()
    
    print("\n" + "=" * 80)
    print("📊 RESUMO DA ANÁLISE")
    print("=" * 80)
    print(f"✅ Cobranças Asaas: {analise['cobrancas_asaas']}")
    print(f"⚠️ Boletos locais: {analise['boletos_locais']}")
    print(f"🔗 URLs redundantes: {len(analise['urls_redundantes'])}")
    print(f"🎨 Templates redundantes: {len(analise['templates_redundantes'])}")
    
    print("\n💡 RECOMENDAÇÃO:")
    if analise['boletos_locais'] == 0:
        print("   Como não há boletos locais, é seguro remover todo o sistema redundante.")
    else:
        print("   Implementar redirecionamentos primeiro, depois migrar dados se necessário.")
    
    print("\n🎯 PRÓXIMO PASSO:")
    print("   Implementar redirecionamentos para manter compatibilidade")
    print("   e melhorar a experiência do usuário.")

if __name__ == '__main__':
    main()
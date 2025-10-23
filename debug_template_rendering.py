#!/usr/bin/env python
"""
Script para debugar problemas de renderização de template
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from django.template.loader import render_to_string
from django.template import Context, Template
from controle_financeiro.models import ControleFinanceiro

def debug_template_rendering():
    """Debug da renderização de templates"""
    
    try:
        # Pegar um controle financeiro para teste
        controle = ControleFinanceiro.objects.first()
        
        if not controle:
            print("❌ Nenhum controle financeiro encontrado")
            return
        
        print(f"✅ Testando com controle: {controle.id}")
        print(f"   Loja: {controle.loja.nome}")
        print(f"   CNPJ: {controle.loja.cnpj}")
        print(f"   Plano: {controle.plano.nome}")
        print(f"   Valor: R$ {controle.valor_mensal}")
        print(f"   Vencimento: {controle.data_vencimento}")
        
        # Testar renderização de template simples
        template_content = """
        <div>
            <h3>{{ controle.loja.nome }}</h3>
            <p>CNPJ: {{ controle.loja.cnpj }}</p>
            <p>Plano: {{ controle.plano.nome }}</p>
            <p>Status: {{ controle.status }}</p>
            <p>Valor Mensal: R$ {{ controle.valor_mensal|floatformat:2 }}</p>
            <p>Vencimento: {{ controle.data_vencimento|date:"d/m/Y" }}</p>
        </div>
        """
        
        template = Template(template_content)
        context = Context({'controle': controle})
        rendered = template.render(context)
        
        print(f"\n📋 Template renderizado:")
        print(rendered)
        
        # Verificar se há caracteres especiais ou problemas de encoding
        print(f"\n🔍 Análise de caracteres:")
        for i, char in enumerate(rendered):
            if ord(char) > 127 or char in ['\n', '\r', '\t']:
                print(f"   Posição {i}: '{char}' (ord: {ord(char)})")
        
        # Testar renderização sem espaços
        rendered_no_spaces = rendered.replace(' ', '').replace('\n', '').replace('\t', '')
        print(f"\n📋 Template sem espaços:")
        print(rendered_no_spaces[:200] + "..." if len(rendered_no_spaces) > 200 else rendered_no_spaces)
        
        return rendered
        
    except Exception as e:
        print(f"❌ Erro no debug: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    debug_template_rendering()
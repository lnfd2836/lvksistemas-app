#!/usr/bin/env python
"""
Script para corrigir a data de vencimento de uma loja específica
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

from controle_financeiro.models import ControleFinanceiro
from django.utils import timezone

def corrigir_vencimento_loja(controle_id, dia_vencimento=4):
    """
    Corrige a data de vencimento de uma loja específica
    
    Args:
        controle_id: ID do controle financeiro
        dia_vencimento: Dia do mês para vencimento (padrão: 4)
    """
    try:
        controle = ControleFinanceiro.objects.get(id=controle_id)
        
        print(f"Controle encontrado: {controle.loja.nome}")
        print(f"Data atual de vencimento: {controle.data_vencimento}")
        
        # Calcular nova data de vencimento para o dia especificado
        agora = timezone.now()
        
        # Criar data com o dia de vencimento desejado
        try:
            nova_data = agora.replace(day=dia_vencimento)
            
            # Se o dia já passou neste mês, usar o próximo mês
            if nova_data <= agora:
                if nova_data.month == 12:
                    nova_data = nova_data.replace(year=nova_data.year + 1, month=1)
                else:
                    nova_data = nova_data.replace(month=nova_data.month + 1)
        except ValueError:
            # Se o dia não existe no mês (ex: 31 em fevereiro), usar o último dia do mês
            from calendar import monthrange
            ultimo_dia = monthrange(agora.year, agora.month)[1]
            nova_data = agora.replace(day=min(dia_vencimento, ultimo_dia))
            if nova_data <= agora:
                if nova_data.month == 12:
                    nova_data = nova_data.replace(year=nova_data.year + 1, month=1, day=dia_vencimento)
                else:
                    nova_data = nova_data.replace(month=nova_data.month + 1, day=dia_vencimento)
        
        controle.data_vencimento = nova_data
        controle.save()
        
        print(f"Nova data de vencimento: {controle.data_vencimento.strftime('%d/%m/%Y')}")
        print(f"Dias para vencimento: {controle.dias_para_vencimento}")
        
    except ControleFinanceiro.DoesNotExist:
        print(f"Controle financeiro com ID {controle_id} não encontrado")
        return False
    except Exception as e:
        print(f"Erro: {str(e)}")
        return False
    
    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python corrigir_vencimento_loja.py <controle_id> [dia_vencimento]")
        print("Exemplo: python corrigir_vencimento_loja.py 148 4")
        sys.exit(1)
    
    controle_id = int(sys.argv[1])
    dia_vencimento = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    
    corrigir_vencimento_loja(controle_id, dia_vencimento)


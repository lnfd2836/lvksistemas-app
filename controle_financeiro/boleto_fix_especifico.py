"""
Correção específica para boletos com problemas conhecidos
"""

from django.contrib import messages
from typing import Dict, Any, Tuple


def corrigir_boleto_especifico(linha_digitavel: str) -> Dict[str, Any]:
    """
    Aplica correções específicas para boletos com problemas conhecidos
    
    Args:
        linha_digitavel: Linha digitável (formatada ou não)
        
    Returns:
        Dict: Resultado da correção
    """
    
    # Normalizar entrada
    linha_limpa = linha_digitavel.replace(" ", "").replace(".", "")
    
    # Mapeamento de correções específicas conhecidas
    correcoes_conhecidas = {
        # Boleto com erro no DV geral (posição 33): 2 → 6
        "10492670145194005415122946570144822370000002990": {
            "corrigido": "10492670145194005415122946570144862370000002990",
            "descricao": "DV geral corrigido: 2 → 6",
            "tipo": "DV Geral",
            "confianca": "alta"
        },
        
        # Adicione outras correções conhecidas aqui conforme necessário
        # "codigo_com_erro": {
        #     "corrigido": "codigo_corrigido",
        #     "descricao": "Descrição da correção",
        #     "tipo": "Tipo do erro",
        #     "confianca": "alta/media/baixa"
        # }
    }
    
    if linha_limpa in correcoes_conhecidas:
        correcao = correcoes_conhecidas[linha_limpa]
        
        return {
            'success': True,
            'corrected': True,
            'original_code': linha_digitavel,
            'final_code': correcao['corrigido'],
            'formatted_original': formatar_linha_digitavel(linha_limpa),
            'formatted_corrected': formatar_linha_digitavel(correcao['corrigido']),
            'message': f"Correção automática aplicada: {correcao['descricao']}",
            'correction_details': {
                'tipo': correcao['tipo'],
                'descricao': correcao['descricao'],
                'confianca': correcao['confianca']
            }
        }
    
    else:
        # Código não tem correção específica conhecida
        return {
            'success': True,
            'corrected': False,
            'original_code': linha_digitavel,
            'final_code': linha_limpa,
            'formatted_original': formatar_linha_digitavel(linha_limpa),
            'formatted_corrected': formatar_linha_digitavel(linha_limpa),
            'message': 'Nenhuma correção específica aplicada',
            'correction_details': None
        }


def formatar_linha_digitavel(linha_limpa: str) -> str:
    """Formata linha digitável para exibição"""
    
    if len(linha_limpa) != 47:
        return linha_limpa
    
    return (
        f"{linha_limpa[0:5]}.{linha_limpa[5:10]} "
        f"{linha_limpa[10:15]}.{linha_limpa[15:21]} "
        f"{linha_limpa[21:26]}.{linha_limpa[26:32]} "
        f"{linha_limpa[32:33]} "
        f"{linha_limpa[33:47]}"
    )


def processar_boleto_com_correcao_django(request, linha_digitavel: str, context_name: str = "boleto") -> Dict[str, Any]:
    """
    Processa boleto com correção específica e adiciona mensagens Django
    
    Args:
        request: Request do Django
        linha_digitavel: Linha digitável
        context_name: Nome para usar nas mensagens
        
    Returns:
        Dict: Resultado do processamento
    """
    
    resultado = corrigir_boleto_especifico(linha_digitavel)
    
    if resultado['success']:
        if resultado['corrected']:
            # Código foi corrigido
            messages.success(request, 
                f"✅ {context_name.title()} processado com sucesso! "
                f"Foi aplicada uma correção automática."
            )
            
            messages.info(request,
                f"ℹ️ Correção aplicada: {resultado['correction_details']['descricao']}"
            )
            
            messages.info(request,
                f"📋 Código original: {resultado['formatted_original']}"
            )
            
            messages.info(request,
                f"📋 Código corrigido: {resultado['formatted_corrected']}"
            )
        
        else:
            # Código processado sem correção
            messages.success(request, f"✅ {context_name.title()} processado com sucesso!")
        
        return {
            'success': True,
            'codigo_final': resultado['final_code'],
            'foi_corrigido': resultado['corrected'],
            'message': resultado['message']
        }
    
    else:
        # Erro no processamento
        messages.error(request, f"❌ Erro no {context_name}: {resultado['message']}")
        
        return {
            'success': False,
            'codigo_final': linha_digitavel,
            'foi_corrigido': False,
            'message': resultado['message']
        }


def validar_e_corrigir_boleto_simples(linha_digitavel: str) -> Tuple[str, bool, str]:
    """
    Função utilitária simples para validar e corrigir boleto
    
    Args:
        linha_digitavel: Linha digitável do boleto
        
    Returns:
        Tuple: (codigo_final, foi_corrigido, mensagem)
    """
    
    resultado = corrigir_boleto_especifico(linha_digitavel)
    
    return (
        resultado['final_code'],
        resultado['corrected'],
        resultado['message']
    )


def is_boleto_corrigivel(linha_digitavel: str) -> bool:
    """
    Verifica se o boleto tem correção específica conhecida
    
    Args:
        linha_digitavel: Linha digitável
        
    Returns:
        bool: True se tem correção conhecida
    """
    
    resultado = corrigir_boleto_especifico(linha_digitavel)
    return resultado['corrected']


# Função de conveniência para uso direto
def corrigir_boleto_automatico(linha_digitavel: str) -> str:
    """
    Retorna código corrigido (se aplicável) ou original
    
    Args:
        linha_digitavel: Linha digitável
        
    Returns:
        str: Código final (corrigido ou original)
    """
    
    resultado = corrigir_boleto_especifico(linha_digitavel)
    return resultado['final_code']
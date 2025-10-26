"""
Utilitários para vinculação automática de administradores de loja
Garante isolamento total entre lojas diferentes
"""
import logging
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


def vincular_admin_loja(loja, admin_user):
    """
    Vincula um usuário administrador a uma loja específica
    Garante isolamento total entre lojas
    
    Args:
        loja: Instância da loja
        admin_user: Usuário que será o administrador
        
    Returns:
        dict: Resultado da operação com sucesso/erro
    """
    try:
        with transaction.atomic():
            # Verificar se o usuário já é admin de outra loja
            if hasattr(admin_user, 'loja_admin') and admin_user.loja_admin != loja:
                return {
                    'success': False,
                    'message': f'Usuário {admin_user.username} já é administrador de outra loja: {admin_user.loja_admin.nome}'
                }
            
            # Verificar se a loja já tem outro admin
            if loja.admin_user and loja.admin_user != admin_user:
                return {
                    'success': False,
                    'message': f'Loja {loja.nome} já tem outro administrador: {loja.admin_user.username}'
                }
            
            # Fazer a vinculação
            loja.admin_user = admin_user
            loja.save()
            
            # Log da operação
            logger.info(f"✅ Admin {admin_user.username} vinculado à loja {loja.nome} com sucesso")
            
            return {
                'success': True,
                'message': f'Administrador {admin_user.username} vinculado à loja {loja.nome} com sucesso'
            }
            
    except Exception as e:
        logger.error(f"❌ Erro ao vincular admin {admin_user.username} à loja {loja.nome}: {str(e)}")
        return {
            'success': False,
            'message': f'Erro ao vincular administrador: {str(e)}'
        }


def criar_perfil_fatesa_se_necessario(loja, admin_user):
    """
    Cria perfil FATESA apenas para a loja específica "Fatesa Escola de Ultrassonografia"
    
    Args:
        loja: Instância da loja
        admin_user: Usuário administrador
        
    Returns:
        dict: Resultado da operação
    """
    try:
        # Verificar se é a loja FATESA específica
        if loja.nome != 'Fatesa Escola de Ultrassonografia':
            return {
                'success': True,
                'message': 'Loja não é FATESA, perfil não criado (normal)',
                'perfil_criado': False
            }
        
        # Verificar se já existe perfil FATESA
        if hasattr(admin_user, 'perfil_fatesa'):
            # Verificar se o perfil está associado à loja correta
            if admin_user.perfil_fatesa.loja_associada != loja:
                logger.warning(f"⚠️  Perfil FATESA de {admin_user.username} está associado a loja diferente")
                # Atualizar a associação
                admin_user.perfil_fatesa.loja_associada = loja
                admin_user.perfil_fatesa.save()
                logger.info(f"✅ Perfil FATESA de {admin_user.username} reasociado à loja {loja.nome}")
            
            return {
                'success': True,
                'message': 'Perfil FATESA já existe e está correto',
                'perfil_criado': False
            }
        
        # Criar perfil FATESA
        from avaliacao_qualidade.models import PerfilUsuario
        
        with transaction.atomic():
            perfil_fatesa = PerfilUsuario.objects.create(
                user=admin_user,
                tipo_perfil='diretoria',
                nome_completo=f'{admin_user.first_name} {admin_user.last_name}'.strip() or admin_user.username,
                telefone=loja.telefone or '',
                ativo=True,
                loja_associada=loja,
                deve_alterar_senha=False
            )
            
            logger.info(f"✅ Perfil FATESA criado para {admin_user.username} na loja {loja.nome}")
            
            return {
                'success': True,
                'message': f'Perfil FATESA criado com sucesso para {admin_user.username}',
                'perfil_criado': True,
                'perfil_id': str(perfil_fatesa.id)
            }
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar perfil FATESA para {admin_user.username}: {str(e)}")
        return {
            'success': False,
            'message': f'Erro ao criar perfil FATESA: {str(e)}',
            'perfil_criado': False
        }


def verificar_isolamento_loja(loja):
    """
    Verifica se a loja está corretamente isolada (sem mistura de dados)
    
    Args:
        loja: Instância da loja
        
    Returns:
        dict: Resultado da verificação
    """
    try:
        problemas = []
        
        # Verificar se o admin está vinculado corretamente
        if not loja.admin_user:
            problemas.append("Loja não tem administrador vinculado")
        elif hasattr(loja.admin_user, 'loja_admin') and loja.admin_user.loja_admin != loja:
            problemas.append(f"Admin {loja.admin_user.username} está vinculado a loja diferente")
        
        # Verificar perfil FATESA se for a loja FATESA
        if loja.nome == 'Fatesa Escola de Ultrassonografia':
            if loja.admin_user and hasattr(loja.admin_user, 'perfil_fatesa'):
                perfil = loja.admin_user.perfil_fatesa
                if perfil.loja_associada != loja:
                    problemas.append(f"Perfil FATESA está associado a loja diferente: {perfil.loja_associada}")
            elif loja.admin_user:
                problemas.append("Loja FATESA sem perfil FATESA criado")
        
        # Verificar se não há outros usuários com acesso a esta loja
        from django.contrib.auth.models import User
        outros_admins = User.objects.filter(loja_admin=loja).exclude(id=loja.admin_user.id if loja.admin_user else None)
        if outros_admins.exists():
            problemas.append(f"Outros usuários com acesso à loja: {[u.username for u in outros_admins]}")
        
        return {
            'success': len(problemas) == 0,
            'problemas': problemas,
            'loja_nome': loja.nome,
            'admin_username': loja.admin_user.username if loja.admin_user else None
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar isolamento da loja {loja.nome}: {str(e)}")
        return {
            'success': False,
            'problemas': [f'Erro na verificação: {str(e)}'],
            'loja_nome': loja.nome
        }


def corrigir_vinculacao_automatica(loja_id):
    """
    Corrige automaticamente problemas de vinculação de uma loja específica
    
    Args:
        loja_id: ID da loja para corrigir
        
    Returns:
        dict: Resultado das correções
    """
    try:
        from lojas.models import Loja
        
        loja = Loja.objects.get(id=loja_id)
        resultados = []
        
        # Verificar isolamento atual
        verificacao = verificar_isolamento_loja(loja)
        if verificacao['success']:
            return {
                'success': True,
                'message': f'Loja {loja.nome} já está corretamente configurada',
                'acoes_realizadas': []
            }
        
        # Corrigir vinculação do admin
        if loja.admin_user:
            resultado_vinculacao = vincular_admin_loja(loja, loja.admin_user)
            resultados.append(f"Vinculação admin: {resultado_vinculacao['message']}")
            
            # Criar perfil FATESA se necessário
            resultado_fatesa = criar_perfil_fatesa_se_necessario(loja, loja.admin_user)
            resultados.append(f"Perfil FATESA: {resultado_fatesa['message']}")
        
        # Verificar novamente
        verificacao_final = verificar_isolamento_loja(loja)
        
        return {
            'success': verificacao_final['success'],
            'message': f'Correções aplicadas para loja {loja.nome}',
            'acoes_realizadas': resultados,
            'problemas_restantes': verificacao_final.get('problemas', [])
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao corrigir vinculação da loja {loja_id}: {str(e)}")
        return {
            'success': False,
            'message': f'Erro ao corrigir vinculação: {str(e)}',
            'acoes_realizadas': []
        }


def listar_lojas_com_problemas():
    """
    Lista todas as lojas que têm problemas de vinculação
    
    Returns:
        list: Lista de lojas com problemas
    """
    try:
        from lojas.models import Loja
        
        lojas_com_problemas = []
        
        for loja in Loja.objects.all():
            verificacao = verificar_isolamento_loja(loja)
            if not verificacao['success']:
                lojas_com_problemas.append({
                    'loja_id': str(loja.id),
                    'loja_nome': loja.nome,
                    'problemas': verificacao['problemas']
                })
        
        return lojas_com_problemas
        
    except Exception as e:
        logger.error(f"❌ Erro ao listar lojas com problemas: {str(e)}")
        return []
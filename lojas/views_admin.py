from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction, DatabaseError, ProgrammingError, connection
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Loja, Cliente, Produto, Venda, Funcionario
from dashboard.services.authentication import AuthenticationService
import logging

logger = logging.getLogger(__name__)


def require_super_admin(view_func):
    """Decorator para views que requerem super admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        if not request.user.is_superuser:
            messages.error(request, 'Apenas Super Administradores podem acessar esta área.')
            return redirect('dashboard:principal')
        
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@require_super_admin
def confirmar_exclusao_loja(request, loja_id):
    """View para confirmar exclusão de loja com aviso detalhado"""
    
    loja = get_object_or_404(Loja, id=loja_id)
    
    if request.method == 'POST':
        if 'confirmar_exclusao' in request.POST:
            return executar_exclusao_loja(request, loja)
        else:
            messages.info(request, 'Exclusão cancelada.')
            return redirect('admin:lojas_loja_changelist')
    
    # Coletar estatísticas da loja para mostrar o que será perdido
    estatisticas = coletar_estatisticas_loja(loja)
    
    context = {
        'loja': loja,
        'estatisticas': estatisticas,
        'titulo': f'Confirmar Exclusão - {loja.nome}',
    }
    
    return render(request, 'admin/lojas/confirmar_exclusao_loja.html', context)


def coletar_estatisticas_loja(loja):
    """Coleta estatísticas detalhadas da loja para mostrar o impacto da exclusão"""
    
    try:
        # Dados básicos
        total_clientes = Cliente.objects.filter(loja=loja).count()
        total_produtos = Produto.objects.filter(loja=loja).count()
        total_vendas = Venda.objects.filter(loja=loja).count()
        total_funcionarios = Funcionario.objects.filter(loja=loja).count()
        
        # Dados financeiros
        from django.db.models import Sum
        receita_total = Venda.objects.filter(
            loja=loja, 
            status='concluida'
        ).aggregate(total=Sum('valor_final'))['total'] or 0
        
        # Dados temporais
        primeira_venda = Venda.objects.filter(loja=loja).order_by('data_venda').first()
        ultima_venda = Venda.objects.filter(loja=loja).order_by('-data_venda').first()
        
        # Controle financeiro
        controle_financeiro = None
        try:
            from controle_financeiro.models import ControleFinanceiro
            controle_financeiro = ControleFinanceiro.objects.filter(loja=loja).first()
        except ImportError:
            pass
        
        # Notificações
        from dashboard.models import Notificacao
        total_notificacoes = Notificacao.objects.filter(loja=loja).count()
        
        # Dados específicos por tipo de loja
        dados_especificos = {}
        
        if loja.tipo_loja and loja.tipo_loja.nome == 'controle_qualidade':
            # Dados específicos do FATESA
            try:
                from avaliacao_qualidade.models import AvaliacaoResposta, Curso
                total_avaliacoes = AvaliacaoResposta.objects.count()  # Se houver filtro por loja
                total_cursos = Curso.objects.count()  # Se houver filtro por loja
                dados_especificos = {
                    'tipo': 'FATESA - Controle de Qualidade',
                    'avaliacoes': total_avaliacoes,
                    'cursos': total_cursos
                }
            except ImportError:
                dados_especificos = {'tipo': 'FATESA - Controle de Qualidade'}
        
        elif loja.tipo_loja and loja.tipo_loja.nome == 'lanchonete':
            # Dados específicos de lanchonete
            from .models import Mesa, Pedido
            total_mesas = Mesa.objects.filter(loja=loja).count()
            total_pedidos = Pedido.objects.filter(loja=loja).count()
            dados_especificos = {
                'tipo': 'Lanchonete',
                'mesas': total_mesas,
                'pedidos': total_pedidos
            }
        
        return {
            'clientes': total_clientes,
            'produtos': total_produtos,
            'vendas': total_vendas,
            'funcionarios': total_funcionarios,
            'receita_total': receita_total,
            'notificacoes': total_notificacoes,
            'primeira_venda': primeira_venda,
            'ultima_venda': ultima_venda,
            'controle_financeiro': controle_financeiro,
            'dados_especificos': dados_especificos,
            'admin_user': loja.admin_user,
        }
        
    except Exception as e:
        logger.error(f"Erro ao coletar estatísticas da loja {loja.nome}: {e}")
        return {
            'erro': 'Não foi possível coletar todas as estatísticas',
            'clientes': 0,
            'produtos': 0,
            'vendas': 0,
            'funcionarios': 0,
        }


def executar_exclusao_loja(request, loja):
    """Executa a exclusão completa da loja e todos os seus dados"""
    
    nome_loja = loja.nome
    loja_id = str(loja.id)
    
    try:
        admin_user = loja.admin_user
        
        logger.info(f"Iniciando exclusão da loja {nome_loja} por super admin {request.user.username}")
        
        # Coletar estatísticas antes da exclusão para log
        stats = coletar_estatisticas_loja(loja)
        
        # Configurações específicas da loja (modulos.ConfiguracaoLoja)
        # Exclui ANTES do bloco atômico para evitar quebrar a transação se a tabela não existir
        configuracoes_removidas = 0
        try:
            from modulos.models import ConfiguracaoLoja
            # Verifica se a tabela existe antes de tentar excluir
            table_name = ConfiguracaoLoja._meta.db_table
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = %s
                        )
                    """, [table_name])
                else:  # SQLite
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT name FROM sqlite_master 
                            WHERE type='table' AND name = ?
                        )
                    """, [table_name])
                table_exists = cursor.fetchone()[0]
            
            if table_exists:
                configuracoes_removidas = ConfiguracaoLoja.objects.filter(loja=loja).delete()[0]
        except (DatabaseError, ProgrammingError) as e:
            error_msg = str(e)
            if 'does not exist' in error_msg or 'relation' in error_msg.lower():
                logger.warning(f"Tabela modulos_configuracaoloja não existe. Pulando exclusão de configurações.")
            else:
                logger.warning(f"Erro ao excluir configurações da loja {loja.nome}: {e}")
            configuracoes_removidas = 0
        except Exception as e:
            logger.warning(f"Não foi possível excluir configurações da loja {loja.nome}: {e}")
            configuracoes_removidas = 0
        
        # Agora executa o resto da exclusão dentro de uma transação atômica
        with transaction.atomic():
            # 1. Excluir dados relacionados (em ordem de dependência)
            
            # Notificações da loja
            from dashboard.models import Notificacao
            notificacoes_removidas = Notificacao.objects.filter(loja=loja).delete()[0]
            
            # Controle financeiro
            try:
                from controle_financeiro.models import ControleFinanceiro
                controle_removido = ControleFinanceiro.objects.filter(loja=loja).delete()[0]
            except ImportError:
                controle_removido = 0
            
            # Itens de venda (antes das vendas)
            from .models import ItemVenda
            itens_removidos = ItemVenda.objects.filter(venda__loja=loja).delete()[0]
            
            # Vendas
            vendas_removidas = Venda.objects.filter(loja=loja).delete()[0]
            
            # Funcionários (isso também remove os usuários associados se CASCADE)
            funcionarios_removidos = Funcionario.objects.filter(loja=loja).delete()[0]
            
            # Produtos
            produtos_removidos = Produto.objects.filter(loja=loja).delete()[0]
            
            # Clientes
            clientes_removidos = Cliente.objects.filter(loja=loja).delete()[0]
            
            # Dados específicos por tipo de loja
            if loja.tipo_loja and loja.tipo_loja.nome == 'lanchonete':
                from .models import Mesa, Pedido, ItemPedido
                ItemPedido.objects.filter(pedido__loja=loja).delete()
                Pedido.objects.filter(loja=loja).delete()
                Mesa.objects.filter(loja=loja).delete()
            
            # 2. Excluir a loja (isso NÃO exclui mais o admin_user devido ao SET_NULL)
            # Como já excluímos manualmente as ConfiguracaoLoja, o CASCADE não deve tentar excluir novamente
            loja.delete()
            
            # 3. Log detalhado da exclusão
            logger.info(f"""
            Loja '{nome_loja}' excluída com sucesso por {request.user.username}:
            - {clientes_removidos} clientes removidos
            - {produtos_removidos} produtos removidos
            - {vendas_removidas} vendas removidas
            - {itens_removidos} itens de venda removidos
            - {funcionarios_removidos} funcionários removidos
            - {notificacoes_removidas} notificações removidas
            - {controle_removido} controles financeiros removidos
            - Admin da loja: {admin_user.username if admin_user else 'Nenhum'} (preservado)
            """)
            
            # 4. Mensagem de sucesso detalhada
            messages.success(
                request, 
                f'Loja "{nome_loja}" excluída com sucesso! '
                f'Foram removidos: {clientes_removidos} clientes, '
                f'{produtos_removidos} produtos, {vendas_removidas} vendas, '
                f'{funcionarios_removidos} funcionários e todos os dados relacionados.'
            )
            
            return redirect('admin:lojas_loja_changelist')
            
    except (DatabaseError, ProgrammingError) as e:
        error_msg = str(e)
        if 'modulos_configuracaoloja' in error_msg or ('does not exist' in error_msg and 'relation' in error_msg.lower()):
            # Se o erro for de tabela não existir, tenta excluir novamente
            # Primeiro garante que ConfiguracaoLoja está excluída antes de excluir a loja
            try:
                # Tenta excluir ConfiguracaoLoja antes, verificando se a tabela existe
                from modulos.models import ConfiguracaoLoja
                table_name = ConfiguracaoLoja._meta.db_table
                table_exists = False
                try:
                    with connection.cursor() as cursor:
                        if connection.vendor == 'postgresql':
                            cursor.execute("""
                                SELECT EXISTS (
                                    SELECT FROM information_schema.tables 
                                    WHERE table_schema = 'public' 
                                    AND table_name = %s
                                )
                            """, [table_name])
                        else:  # SQLite
                            cursor.execute("""
                                SELECT EXISTS (
                                    SELECT name FROM sqlite_master 
                                    WHERE type='table' AND name = ?
                                )
                            """, [table_name])
                        table_exists = cursor.fetchone()[0]
                except Exception as check_error:
                    logger.warning(f"Erro ao verificar existência da tabela {table_name}: {check_error}")
                    table_exists = False
                
                if table_exists:
                    try:
                        ConfiguracaoLoja.objects.filter(loja=loja).delete()
                    except (DatabaseError, ProgrammingError) as delete_error:
                        error_msg = str(delete_error)
                        if 'does not exist' in error_msg or 'relation' in error_msg.lower():
                            logger.warning(f"Tabela {table_name} não existe durante exclusão. Continuando...")
                        else:
                            logger.warning(f"Erro ao excluir ConfiguracaoLoja: {delete_error}")
                    except Exception as delete_error:
                        logger.warning(f"Erro inesperado ao excluir ConfiguracaoLoja: {delete_error}")
                
                # Agora exclui a loja manualmente, removendo todos os dados relacionados primeiro
                from dashboard.models import Notificacao
                from .models import ItemVenda
                notificacoes_removidas = Notificacao.objects.filter(loja=loja).delete()[0]
                try:
                    from controle_financeiro.models import ControleFinanceiro
                    ControleFinanceiro.objects.filter(loja=loja).delete()
                except ImportError:
                    pass
                ItemVenda.objects.filter(venda__loja=loja).delete()
                Venda.objects.filter(loja=loja).delete()
                Funcionario.objects.filter(loja=loja).delete()
                Produto.objects.filter(loja=loja).delete()
                Cliente.objects.filter(loja=loja).delete()
                if loja.tipo_loja and loja.tipo_loja.nome == 'lanchonete':
                    from .models import Mesa, Pedido, ItemPedido
                    ItemPedido.objects.filter(pedido__loja=loja).delete()
                    Pedido.objects.filter(loja=loja).delete()
                    Mesa.objects.filter(loja=loja).delete()
                # Verifica se admin_user ainda existe e tem ID válido antes de excluir
                # Como o relacionamento usa SET_NULL, não precisamos excluir o admin_user
                # Mas se quisermos excluir, precisamos verificar se ainda tem ID
                # Na verdade, pela migração anterior, admin_user deve ser preservado (SET_NULL)
                # então não excluímos ele aqui
                loja.delete()
                
                logger.warning(f"Loja excluída manualmente após erro de tabela modulos_configuracaoloja não existir.")
                messages.success(request, f'Loja "{nome_loja}" excluída com sucesso!')
                return redirect('admin:lojas_loja_changelist')
            except Exception as e2:
                logger.error(f"Erro ao excluir loja {nome_loja} na segunda tentativa: {e2}")
                messages.error(request, f'Erro ao excluir a loja: {str(e2)}. Verifique os logs.')
        else:
            logger.error(f"Erro ao excluir loja {nome_loja}: {e}")
            messages.error(request, f'Erro ao excluir a loja: {str(e)}. Verifique os logs.')
        return redirect('admin:lojas_loja_changelist')
            
    except Exception as e:
        logger.error(f"Erro ao excluir loja {loja.nome if 'loja' in locals() else 'desconhecida'}: {e}")
        messages.error(
            request, 
            f'Erro ao excluir a loja: {str(e)}. '
            'Verifique os logs para mais detalhes.'
        )
        return redirect('admin:lojas_loja_changelist')


@login_required
@require_super_admin
@require_http_methods(["POST"])
def exclusao_rapida_loja(request, loja_id):
    """Exclusão rápida via AJAX para o admin"""
    
    try:
        loja = get_object_or_404(Loja, id=loja_id)
        
        # Coletar estatísticas básicas
        stats = coletar_estatisticas_loja(loja)
        
        # Executar exclusão
        with transaction.atomic():
            nome_loja = loja.nome
            
            # Exclui configurações manualmente antes para evitar erro de CASCADE
            try:
                from modulos.models import ConfiguracaoLoja
                from django.db import DatabaseError, ProgrammingError
                ConfiguracaoLoja.objects.filter(loja=loja).delete()
            except (DatabaseError, ProgrammingError) as e:
                error_msg = str(e)
                if 'does not exist' in error_msg or 'relation' in error_msg.lower():
                    logger.warning(f"Tabela modulos_configuracaoloja não existe. Pulando exclusão de configurações.")
                else:
                    logger.warning(f"Erro ao excluir configurações da loja {loja.nome}: {e}")
            except Exception as e:
                logger.warning(f"Não foi possível excluir configurações da loja {loja.nome}: {e}")
            
            # Exclui a loja
            loja.delete()
            
            logger.info(f"Exclusão rápida da loja {nome_loja} por {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': f'Loja "{nome_loja}" excluída com sucesso!',
            'stats': {
                'clientes': stats.get('clientes', 0),
                'produtos': stats.get('produtos', 0),
                'vendas': stats.get('vendas', 0),
            }
        })
        
    except Exception as e:
        logger.error(f"Erro na exclusão rápida da loja: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
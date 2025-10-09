"""
Tarefas assíncronas do Celery
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Loja, BackupLoja
from lojad.database_utils import criar_backup_loja, otimizar_banco_loja
from usuarios.models import LogAcesso
from dashboard.models import Notificacao


@shared_task
def backup_diario():
    """
    Cria backup diário de todas as lojas ativas
    """
    lojas_ativas = Loja.objects.filter(status='ativa')
    
    for loja in lojas_ativas:
        try:
            sucesso, resultado = criar_backup_loja(loja)
            
            if sucesso:
                # Registra o backup
                BackupLoja.objects.create(
                    loja=loja,
                    nome_arquivo=f"backup_{loja.db_name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sql",
                    tamanho_arquivo=0,  # Será calculado depois
                    caminho_arquivo=resultado,
                    sucesso=True,
                    observacoes="Backup diário automático"
                )
                
                # Cria notificação
                Notificacao.objects.create(
                    titulo=f"Backup diário - {loja.nome}",
                    mensagem=f"Backup da loja {loja.nome} criado com sucesso.",
                    tipo='success',
                    prioridade='baixa',
                    loja=loja
                )
            else:
                # Registra o erro
                BackupLoja.objects.create(
                    loja=loja,
                    nome_arquivo=f"backup_{loja.db_name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sql",
                    tamanho_arquivo=0,
                    caminho_arquivo="",
                    sucesso=False,
                    observacoes=f"Erro: {resultado}"
                )
                
                # Cria notificação de erro
                Notificacao.objects.create(
                    titulo=f"Erro no backup - {loja.nome}",
                    mensagem=f"Erro ao criar backup da loja {loja.nome}: {resultado}",
                    tipo='error',
                    prioridade='alta',
                    loja=loja
                )
                
        except Exception as e:
            # Cria notificação de erro
            Notificacao.objects.create(
                titulo=f"Erro no backup - {loja.nome}",
                mensagem=f"Erro inesperado ao criar backup da loja {loja.nome}: {str(e)}",
                tipo='error',
                prioridade='critica',
                loja=loja
            )


@shared_task
def otimizar_bancos():
    """
    Otimiza todos os bancos de dados das lojas
    """
    lojas = Loja.objects.all()
    
    for loja in lojas:
        try:
            if otimizar_banco_loja(loja):
                # Cria notificação
                Notificacao.objects.create(
                    titulo=f"Otimização concluída - {loja.nome}",
                    mensagem=f"O banco de dados da loja {loja.nome} foi otimizado.",
                    tipo='info',
                    prioridade='baixa',
                    loja=loja
                )
        except Exception as e:
            # Cria notificação de erro
            Notificacao.objects.create(
                titulo=f"Erro na otimização - {loja.nome}",
                mensagem=f"Erro ao otimizar banco da loja {loja.nome}: {str(e)}",
                tipo='error',
                prioridade='media',
                loja=loja
            )


@shared_task
def limpar_logs_antigos():
    """
    Remove logs de acesso antigos (mais de 90 dias)
    """
    data_limite = timezone.now() - timedelta(days=90)
    
    logs_removidos = LogAcesso.objects.filter(
        data_acesso__lt=data_limite
    ).delete()
    
    # Cria notificação
    Notificacao.objects.create(
        titulo="Limpeza de logs",
        mensagem=f"{logs_removidos[0]} logs antigos foram removidos.",
        tipo='info',
        prioridade='baixa'
    )


@shared_task
def backup_loja_especifica(loja_id):
    """
    Cria backup de uma loja específica
    """
    try:
        loja = Loja.objects.get(id=loja_id)
        sucesso, resultado = criar_backup_loja(loja)
        
        if sucesso:
            # Registra o backup
            BackupLoja.objects.create(
                loja=loja,
                nome_arquivo=f"backup_{loja.db_name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sql",
                tamanho_arquivo=0,
                caminho_arquivo=resultado,
                sucesso=True,
                observacoes="Backup sob demanda"
            )
            
            return f"Backup da loja {loja.nome} criado com sucesso"
        else:
            return f"Erro ao criar backup da loja {loja.nome}: {resultado}"
            
    except Loja.DoesNotExist:
        return f"Loja com ID {loja_id} não encontrada"
    except Exception as e:
        return f"Erro inesperado: {str(e)}"


@shared_task
def enviar_email_notificacao(notificacao_id):
    """
    Envia email de notificação
    """
    try:
        notificacao = Notificacao.objects.get(id=notificacao_id)
        
        # Aqui você implementaria o envio de email
        # Por enquanto, apenas retorna sucesso
        
        return f"Email de notificação {notificacao_id} enviado"
        
    except Notificacao.DoesNotExist:
        return f"Notificação {notificacao_id} não encontrada"
    except Exception as e:
        return f"Erro ao enviar email: {str(e)}"








from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction, DatabaseError, ProgrammingError
from django.db.models import Q
from django.utils import timezone
import logging

from .models import Loja, Cliente, Produto, Venda, BackupLoja, ItemVenda
from .forms import LojaForm, ClienteForm, ProdutoForm
from dashboard.models import Notificacao
from controle_financeiro.models import ControleFinanceiro, PlanoFinanceiro, ConfiguracaoBoleto, BoletoGerado
from datetime import timedelta

logger = logging.getLogger(__name__)


def is_superuser(user):
    """Verifica se o usuário é super usuário"""
    return user.is_superuser


@login_required
def listar_lojas(request):
    """Lista todas as lojas do sistema"""
    
    # Se não é super usuário, redireciona para o dashboard da loja
    if not request.user.is_superuser:
        if hasattr(request, 'loja_atual'):
            return redirect('dashboard_loja')
        else:
            messages.error(request, 'Você não tem uma loja associada.')
            return redirect('login')
    
    # Buscar lojas - usar defer para evitar carregar tipo_loja se a tabela não existir
    # Isso previne que o Django tente fazer query quando o template acessar loja.tipo_loja
    lojas = Loja.objects.defer('tipo_loja').all().order_by('-data_criacao')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        lojas = lojas.filter(status=status_filter)
    
    tipo_filter = request.GET.get('tipo_loja')
    if tipo_filter:
        try:
            lojas = lojas.filter(tipo_loja__nome=tipo_filter)
        except (DatabaseError, ProgrammingError) as e:
            logger.warning(f"Erro ao filtrar por tipo_loja: {str(e)}")
            # Se a tabela não existe, simplesmente ignora o filtro
            tipo_filter = None
    
    search = request.GET.get('search')
    if search:
        lojas = lojas.filter(
            Q(nome__icontains=search) |
            Q(cnpj__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Estatísticas por tipo de loja (com tratamento de erro)
    stats_tipos = {}
    try:
        for tipo in ['conveniencia', 'roupas', 'tintas', 'supermercado', 'lanchonete']:
            try:
                stats_tipos[tipo] = Loja.objects.filter(tipo_loja__nome=tipo).count()
            except (DatabaseError, ProgrammingError):
                stats_tipos[tipo] = 0
    except Exception as e:
        logger.warning(f"Erro ao calcular estatísticas por tipo: {str(e)}")
        stats_tipos = {}
    
    context = {
        'lojas': lojas,
        'status_filter': status_filter,
        'tipo_filter': tipo_filter,
        'search': search,
        'stats_tipos': stats_tipos,
    }
    
    return render(request, 'lojas/listar.html', context)


@login_required
@user_passes_test(is_superuser)
def criar_loja(request):
    """Cria uma nova loja"""
    
    # Carregar planos disponíveis para o contexto
    from lojas.utils.plan_mapping import get_available_commercial_plans
    planos_disponiveis = get_available_commercial_plans()
    
    if request.method == 'POST':
        form = LojaForm(request.POST)
        
        if form.is_valid():
            with transaction.atomic():
                # Obter o plano selecionado
                plano_comercial = form.cleaned_data['plano_comercial']
                
                # Cria o usuário administrador da loja
                admin_user = User.objects.create_user(
                    username=form.cleaned_data['email'],
                    email=form.cleaned_data['email'],
                    first_name=form.cleaned_data['nome'].split()[0],
                    last_name=' '.join(form.cleaned_data['nome'].split()[1:]) if len(form.cleaned_data['nome'].split()) > 1 else '',
                    is_staff=True,
                )
                
                # Marca que a senha será definida manualmente para evitar interferência do signal
                admin_user._password_set_manually = True
                
                # Cria a loja (remove plano_comercial dos dados salvos)
                loja = form.save(commit=False)
                loja.admin_user = admin_user
                loja.save()
                
                # Define a senha do usuário administrador
                admin_user.set_password(loja.senha_provisoria)
                admin_user.save()
                
                # Criar perfil do usuário da loja com troca obrigatória de senha
                from usuarios.models import PerfilUsuario
                perfil, created_perfil = PerfilUsuario.objects.get_or_create(
                    user=admin_user,
                    defaults={
                        'requires_password_change': True,
                        'deve_trocar_senha': True,
                        'provisional_password_created': timezone.now(),
                        'is_loja_admin': True,
                        'is_super_admin': False,
                    }
                )
                
                if not created_perfil:
                    # Se o perfil já existia, atualiza os campos necessários
                    perfil.requires_password_change = True
                    perfil.deve_trocar_senha = True
                    perfil.provisional_password_created = timezone.now()
                    perfil.is_loja_admin = True
                    perfil.is_super_admin = False
                    perfil.save()
                
                logger.info(f"Perfil criado para usuário da loja {loja.nome}: {admin_user.username}")
                
                # Obter dia de vencimento escolhido pelo cliente
                dia_vencimento = form.cleaned_data.get('dia_vencimento', None)
                if dia_vencimento:
                    dia_vencimento = int(dia_vencimento)  # Converter para inteiro
                
                # Cria ambos os registros financeiros usando o plano selecionado
                try:
                    from lojas.utils.plan_mapping import create_both_financial_records
                    controle_financeiro, assinatura_loja = create_both_financial_records(
                        loja, plano_comercial, dia_vencimento
                    )
                    
                    # Gera cobrança automaticamente usando o Asaas centralizado
                    try:
                        from controle_financeiro.asaas_central_service import AsaasCentralService
                        
                        asaas_service = AsaasCentralService()
                        
                        # Testar conexão primeiro
                        conexao_test = asaas_service.testar_conexao()
                        if not conexao_test['success']:
                            logger.warning(f"Problema na conexão Asaas: {conexao_test['message']}")
                        
                        # Gerar cobrança no Asaas
                        dias_vencimento = 7  # Padrão 7 dias para primeira cobrança
                        cobranca_asaas = asaas_service.gerar_cobranca_loja(controle_financeiro, dias_vencimento)
                        
                        if cobranca_asaas:
                            logger.info(f"Cobrança Asaas gerada com sucesso para {loja.nome}: {cobranca_asaas['id']}")
                            
                            # Criar notificação sobre a cobrança
                            try:
                                from dashboard.models import Notificacao
                                Notificacao.objects.create(
                                    titulo=f"Cobrança gerada para {loja.nome}",
                                    mensagem=f"Cobrança Asaas {cobranca_asaas['id']} gerada automaticamente. Valor: R$ {controle_financeiro.valor_mensal}",
                                    tipo='info',
                                    prioridade='media',
                                    usuario=request.user
                                )
                            except Exception as notif_error:
                                logger.warning(f"Erro ao criar notificação: {str(notif_error)}")
                        
                    except Exception as asaas_error:
                        # Se houver erro na geração da cobrança, log mas não falha a criação da loja
                        logger.error(f"Erro ao gerar cobrança Asaas para loja {loja.nome}: {str(asaas_error)}")
                        # A loja é criada mesmo se a cobrança falhar
                    
                except Exception as e:
                    # Log do erro e reverte a transação
                    logger.error(f"Erro ao criar registros financeiros para loja {loja.nome}: {str(e)}")
                    messages.error(request, f"Erro ao criar registros financeiros: {str(e)}")
                    return render(request, 'lojas/criar.html', {
                        'form': form,
                        'planos_disponiveis': planos_disponiveis
                    })
                
                # Cria notificação de sucesso
                try:
                    Notificacao.objects.create(
                        titulo=f"Loja {loja.nome} criada com sucesso",
                        mensagem=f"A loja {loja.nome} foi criada com sucesso com o plano {plano_comercial.nome}. Controle financeiro e assinatura gerados automaticamente.",
                        tipo='success',
                        prioridade='media',
                        usuario=request.user
                    )
                except:
                    pass  # Ignora erro se não conseguir criar notificação
                
                # O email com login personalizado será enviado pelo signal automaticamente
                messages.success(
                    request, 
                    f'Loja "{loja.nome}" criada com sucesso com o plano {plano_comercial.nome}! '
                    f'📧 Email com link de acesso personalizado enviado para: {loja.email} | '
                    f'🔑 Senha provisória: {loja.senha_provisoria} | '
                    f'⚠️ IMPORTANTE: O usuário deve alterar a senha no primeiro acesso.'
                )
                
                return redirect('lojas:listar_lojas')
    else:
        form = LojaForm()
    
    context = {
        'form': form,
        'planos_disponiveis': planos_disponiveis
    }
    
    return render(request, 'lojas/criar.html', context)


@login_required
@user_passes_test(is_superuser)
def editar_loja(request, loja_id):
    """Edita uma loja existente"""
    
    loja = get_object_or_404(Loja, id=loja_id)
    
    if request.method == 'POST':
        form = LojaForm(request.POST, instance=loja)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Loja {loja.nome} atualizada com sucesso!')
            return redirect('lojas:listar_lojas')
    else:
        form = LojaForm(instance=loja)
    
    return render(request, 'lojas/editar.html', {'form': form, 'loja': loja})


@login_required
@user_passes_test(is_superuser)
def detalhar_loja(request, loja_id):
    """Detalha uma loja específica"""
    
    try:
        loja = get_object_or_404(Loja, id=loja_id)
        
        # Estatísticas da loja (com tratamento de erro)
        total_clientes = 0
        total_produtos = 0
        total_vendas = 0
        vendas_recentes = []
        backups = []
        
        try:
            total_clientes = Cliente.objects.filter(loja=loja).count()
        except Exception as e:
            logger.warning(f"Erro ao contar clientes da loja {loja.nome}: {str(e)}")
        
        try:
            total_produtos = Produto.objects.filter(loja=loja).count()
        except Exception as e:
            logger.warning(f"Erro ao contar produtos da loja {loja.nome}: {str(e)}")
        
        try:
            total_vendas = Venda.objects.filter(loja=loja).count()
        except Exception as e:
            logger.warning(f"Erro ao contar vendas da loja {loja.nome}: {str(e)}")
        
        # Vendas recentes (com tratamento de erro)
        try:
            vendas_recentes = Venda.objects.filter(loja=loja).order_by('-data_venda')[:10]
        except Exception as e:
            logger.warning(f"Erro ao buscar vendas recentes da loja {loja.nome}: {str(e)}")
            vendas_recentes = []
        
        # Backups da loja (com tratamento de erro)
        try:
            backups = BackupLoja.objects.filter(loja=loja).order_by('-data_backup')[:5]
        except Exception as e:
            logger.warning(f"Erro ao buscar backups da loja {loja.nome}: {str(e)}")
            backups = []
        
        # Informações do plano comercial
        assinatura = None
        plano = None
        dias_vencimento = 0
        limites_atingidos = {}
        
        try:
            from planos.models import AssinaturaLoja
            assinatura = AssinaturaLoja.objects.filter(loja=loja, status='ativa').first()
            if assinatura:
                plano = assinatura.plano
                try:
                    dias_vencimento = assinatura.dias_para_vencimento()
                except:
                    dias_vencimento = 0
                try:
                    limites_atingidos = assinatura.verificar_limites()
                except:
                    limites_atingidos = {}
        except Exception as e:
            logger.warning(f"Erro ao buscar informações do plano para loja {loja.nome}: {str(e)}")
        
        context = {
            'loja': loja,
            'total_clientes': total_clientes,
            'total_produtos': total_produtos,
            'total_vendas': total_vendas,
            'vendas_recentes': vendas_recentes,
            'backups': backups,
            'assinatura': assinatura,
            'plano': plano,
            'dias_vencimento': dias_vencimento,
            'limites_atingidos': limites_atingidos,
        }
        
        return render(request, 'lojas/detalhar.html', context)
        
    except Exception as e:
        logger.error(f"Erro crítico ao detalhar loja {loja_id}: {str(e)}")
        messages.error(request, f'Erro ao carregar detalhes da loja: {str(e)}')
        return redirect('lojas:listar_lojas')




@login_required
@user_passes_test(is_superuser)
def alterar_status_loja(request, loja_id):
    """Altera o status de uma loja"""
    
    loja = get_object_or_404(Loja, id=loja_id)
    novo_status = request.POST.get('status')
    
    if novo_status in ['ativa', 'inativa', 'suspensa']:
        loja.status = novo_status
        loja.save()
        
        # Cria notificação
        Notificacao.objects.create(
            titulo=f"Status da loja {loja.nome} alterado",
            mensagem=f"O status da loja {loja.nome} foi alterado para {loja.get_status_display()}.",
            tipo='info',
            prioridade='media',
            usuario=request.user
        )
        
        messages.success(request, f'Status da loja {loja.nome} alterado para {loja.get_status_display()}.')
    
    return redirect('detalhar_loja', loja_id=loja_id)


@login_required
def gerenciar_clientes(request):
    """Gerencia clientes da loja atual"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    # Buscar clientes com tratamento de erro para tabela ausente
    clientes = []
    total_clientes = 0
    
    try:
        clientes = Cliente.objects.filter(loja=loja).order_by('-data_cadastro')
        
        # Filtros
        search = request.GET.get('search')
        if search:
            clientes = clientes.filter(
                Q(nome__icontains=search) |
                Q(email__icontains=search) |
                Q(cpf__icontains=search)
            )
        
        ativo_filter = request.GET.get('ativo')
        if ativo_filter is not None:
            clientes = clientes.filter(ativo=ativo_filter == 'true')
        
        # Converter para lista para evitar queries lazy no template
        clientes = list(clientes)
        total_clientes = len(clientes)
        search_param = search
        ativo_filter_param = ativo_filter
        
    except (DatabaseError, ProgrammingError) as e:
        logger.warning(f"Tabela lojas_cliente não existe para loja {loja.nome}: {str(e)}")
        messages.warning(request, 'A funcionalidade de clientes não está disponível no momento.')
        clientes = []
        total_clientes = 0
        search_param = request.GET.get('search')
        ativo_filter_param = request.GET.get('ativo')
    except Exception as e:
        logger.error(f"Erro ao buscar clientes para loja {loja.nome}: {str(e)}")
        messages.error(request, 'Erro ao carregar clientes.')
        clientes = []
        total_clientes = 0
        search_param = request.GET.get('search')
        ativo_filter_param = request.GET.get('ativo')
    
    context = {
        'clientes': clientes,
        'total_clientes': total_clientes,
        'loja': loja,
        'search': search_param,
        'ativo_filter': ativo_filter_param,
    }
    
    return render(request, 'lojas/clientes.html', context)


@login_required
def adicionar_cliente(request):
    """Adiciona um novo cliente"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.loja = loja
            cliente.save()
            
            messages.success(request, f'Cliente {cliente.nome} cadastrado com sucesso!')
            return redirect('gerenciar_clientes')
    else:
        form = ClienteForm()
    
    return render(request, 'lojas/adicionar_cliente.html', {'form': form, 'loja': loja})


@login_required
def editar_cliente(request, cliente_id):
    """Edita um cliente existente"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    cliente = get_object_or_404(Cliente, id=cliente_id, loja=loja)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Cliente {cliente.nome} atualizado com sucesso!')
            return redirect('gerenciar_clientes')
    else:
        form = ClienteForm(instance=cliente)
    
    return render(request, 'lojas/editar_cliente.html', {'form': form, 'cliente': cliente, 'loja': loja})


@login_required
def gerenciar_produtos(request):
    """Gerencia produtos da loja atual"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    # Buscar produtos com tratamento de erro para tabela ausente
    produtos = []
    total_produtos = 0
    
    try:
        produtos = Produto.objects.filter(loja=loja).order_by('nome')
        
        # Filtros
        search = request.GET.get('search')
        if search:
            produtos = produtos.filter(
                Q(nome__icontains=search) |
                Q(descricao__icontains=search) |
                Q(codigo_barras__icontains=search)
            )
        
        categoria_filter = request.GET.get('categoria')
        if categoria_filter:
            produtos = produtos.filter(categoria=categoria_filter)
        
        ativo_filter = request.GET.get('ativo')
        if ativo_filter is not None:
            produtos = produtos.filter(ativo=ativo_filter == 'true')
        
        # Converter para lista para evitar queries lazy no template
        produtos = list(produtos)
        total_produtos = len(produtos)
        search_param = search
        categoria_filter_param = categoria_filter
        ativo_filter_param = ativo_filter
        
    except (DatabaseError, ProgrammingError) as e:
        logger.warning(f"Tabela lojas_produto não existe para loja {loja.nome}: {str(e)}")
        messages.warning(request, 'A funcionalidade de produtos não está disponível no momento.')
        produtos = []
        total_produtos = 0
        search_param = request.GET.get('search')
        categoria_filter_param = request.GET.get('categoria')
        ativo_filter_param = request.GET.get('ativo')
    except Exception as e:
        logger.error(f"Erro ao buscar produtos para loja {loja.nome}: {str(e)}")
        messages.error(request, 'Erro ao carregar produtos.')
        produtos = []
        total_produtos = 0
        search_param = request.GET.get('search')
        categoria_filter_param = request.GET.get('categoria')
        ativo_filter_param = request.GET.get('ativo')
    
    context = {
        'produtos': produtos,
        'total_produtos': total_produtos,
        'loja': loja,
        'search': search_param,
        'categoria_filter': categoria_filter_param,
        'ativo_filter': ativo_filter_param,
    }
    
    return render(request, 'lojas/produtos.html', context)


@login_required
def adicionar_produto(request):
    """Adiciona um novo produto"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        
        if form.is_valid():
            produto = form.save(commit=False)
            produto.loja = loja
            produto.save()
            
            messages.success(request, f'Produto {produto.nome} cadastrado com sucesso!')
            return redirect('gerenciar_produtos')
    else:
        form = ProdutoForm()
    
    return render(request, 'lojas/adicionar_produto.html', {'form': form, 'loja': loja})


@login_required
def editar_produto(request, produto_id):
    """Edita um produto existente"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    produto = get_object_or_404(Produto, id=produto_id, loja=loja)
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Produto {produto.nome} atualizado com sucesso!')
            return redirect('gerenciar_produtos')
    else:
        form = ProdutoForm(instance=produto)
    
    return render(request, 'lojas/editar_produto.html', {'form': form, 'produto': produto, 'loja': loja})


@login_required
@user_passes_test(is_superuser)
def backup_loja(request, loja_id):
    """Cria backup de uma loja"""
    
    loja = get_object_or_404(Loja, id=loja_id)
    
    try:
        # Aqui você implementaria a lógica de backup real
        # Por enquanto, apenas simula o backup
        
        backup = BackupLoja.objects.create(
            loja=loja,
            nome_arquivo=f"backup_{loja.db_name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sql",
            tamanho_arquivo=1024000,  # 1MB simulado
            caminho_arquivo=f"/backups/{loja.db_name}/",
            sucesso=True,
            observacoes="Backup criado com sucesso"
        )
        
        # Cria notificação
        Notificacao.objects.create(
            titulo=f"Backup da loja {loja.nome} criado",
            mensagem=f"O backup da loja {loja.nome} foi criado com sucesso.",
            tipo='success',
            prioridade='media',
            usuario=request.user
        )
        
        messages.success(request, f'Backup da loja {loja.nome} criado com sucesso!')
        
    except Exception as e:
        messages.error(request, f'Erro ao criar backup: {str(e)}')
    
    return redirect('lojas:detalhar_loja', loja_id=loja_id)

@login_required
@user_passes_test(is_superuser)
def excluir_loja(request, loja_id):
    """Exclui uma loja e todos os dados relacionados"""
    
    loja = get_object_or_404(Loja, id=loja_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Armazena informações para notificação
                nome_loja = loja.nome
                admin_user = loja.admin_user
                
                # Exclui todos os dados relacionados
                # 1. Exclui vendas e itens de venda
                vendas = Venda.objects.filter(loja=loja)
                for venda in vendas:
                    ItemVenda.objects.filter(venda=venda).delete()
                vendas.delete()
                
                # 2. Exclui produtos
                Produto.objects.filter(loja=loja).delete()
                
                # 3. Exclui clientes
                Cliente.objects.filter(loja=loja).delete()
                
                # 4. Exclui backups
                BackupLoja.objects.filter(loja=loja).delete()
                
                # 5. Exclui notificações relacionadas
                Notificacao.objects.filter(loja=loja).delete()
                
                # 6. Exclui configurações específicas da loja (modulos.ConfiguracaoLoja)
                # Exclui manualmente para evitar erro de CASCADE se a tabela não existir
                try:
                    from modulos.models import ConfiguracaoLoja
                    from django.db import DatabaseError, ProgrammingError
                    ConfiguracaoLoja.objects.filter(loja=loja).delete()
                except (DatabaseError, ProgrammingError) as e:
                    # Se a tabela não existir (especialmente no Heroku antes das migrações),
                    # apenas loga e continua. O CASCADE não acontecerá automaticamente.
                    import logging
                    logger = logging.getLogger(__name__)
                    error_msg = str(e)
                    if 'does not exist' in error_msg or 'relation' in error_msg.lower():
                        logger.warning(f"Tabela modulos_configuracaoloja não existe. Pulando exclusão de configurações.")
                    else:
                        logger.warning(f"Erro ao excluir configurações da loja {loja.nome}: {e}")
                except Exception as e:
                    # Outros erros também são tratados
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Não foi possível excluir configurações da loja {loja.nome}: {e}")
                
                # 7. Exclui usuário administrador
                if admin_user:
                    admin_user.delete()
                
                # 8. Exclui a loja
                # Como já excluímos manualmente as ConfiguracaoLoja, o CASCADE não deve tentar excluir novamente
                loja.delete()
                
                # Cria notificação de sucesso
                try:
                    Notificacao.objects.create(
                        titulo=f"Loja {nome_loja} excluída",
                        mensagem=f"A loja {nome_loja} e todos os dados relacionados foram excluídos com sucesso.",
                        tipo='success',
                        prioridade='alta',
                        usuario=request.user
                    )
                except:
                    pass  # Ignora erro se não conseguir criar notificação
                
                messages.success(request, f'Loja {nome_loja} excluída com sucesso!')
                return redirect('lojas:listar_lojas')
                
        except (DatabaseError, ProgrammingError) as e:
            import logging
            logger = logging.getLogger(__name__)
            error_msg = str(e)
            loja_id_str = str(loja.id)
            if 'modulos_configuracaoloja' in error_msg or ('does not exist' in error_msg and 'relation' in error_msg.lower()):
                # Se o erro for de tabela não existir, tenta excluir novamente após o rollback
                try:
                    Loja.objects.filter(id=loja_id_str).delete()
                    logger.warning(f"Loja excluída via QuerySet após erro de tabela modulos_configuracaoloja não existir.")
                    messages.success(request, f'Loja {nome_loja} excluída com sucesso!')
                    return redirect('lojas:listar_lojas')
                except Exception as e2:
                    logger.error(f"Erro ao excluir loja {nome_loja} na segunda tentativa: {e2}")
                    messages.error(request, f'Erro ao excluir a loja: {str(e2)}. Verifique os logs.')
            else:
                logger.error(f"Erro ao excluir loja {nome_loja}: {e}")
                messages.error(request, f'Erro ao excluir a loja: {str(e)}. Verifique os logs.')
            return redirect('lojas:listar_lojas')
                
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erro ao excluir loja {loja.nome if 'loja' in locals() else 'desconhecida'}: {e}")
            messages.error(request, f'Erro ao excluir loja: {str(e)}')
            return redirect('lojas:listar_lojas')
    
    # Se não for POST, mostra página de confirmação
    context = {
        'loja': loja,
    }
    return render(request, 'lojas/confirmar_exclusao.html', context)


@login_required
def gerenciar_vendas(request):
    """Gerencia as vendas da loja"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    # Buscar vendas com tratamento de erro para tabela ausente
    vendas = []
    total_vendas = 0
    
    try:
        vendas = Venda.objects.filter(loja=loja).order_by('-data_venda')
        
        # Filtros
        status_filter = request.GET.get('status')
        if status_filter:
            vendas = vendas.filter(status=status_filter)
        
        search = request.GET.get('search')
        if search:
            vendas = vendas.filter(
                Q(numero_venda__icontains=search) |
                Q(cliente__nome__icontains=search)
            )
        
        # Converter para lista para evitar queries lazy no template
        vendas = list(vendas)
        total_vendas = len(vendas)
        
    except (DatabaseError, ProgrammingError) as e:
        logger.warning(f"Tabela lojas_venda não existe para loja {loja.nome}: {str(e)}")
        messages.warning(request, 'A funcionalidade de vendas não está disponível no momento.')
        vendas = []
        total_vendas = 0
        status_filter = None
        search = None
    except Exception as e:
        logger.error(f"Erro ao buscar vendas para loja {loja.nome}: {str(e)}")
        messages.error(request, 'Erro ao carregar vendas.')
        vendas = []
        total_vendas = 0
        status_filter = request.GET.get('status')
        search = request.GET.get('search')
    
    context = {
        'vendas': vendas,
        'total_vendas': total_vendas,
        'loja': loja,
        'status_filter': status_filter,
        'search': search,
    }
    
    return render(request, 'lojas/vendas.html', context)


@login_required
def nova_venda(request):
    """Cria uma nova venda"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    if request.method == 'POST':
        # Lógica para criar nova venda
        cliente_id = request.POST.get('cliente')
        produtos_ids = request.POST.getlist('produtos')
        quantidades = request.POST.getlist('quantidades')
        
        try:
            cliente = Cliente.objects.get(id=cliente_id, loja=loja)
            
            # Cria a venda
            venda = Venda.objects.create(
                loja=loja,
                cliente=cliente,
                valor_total=0,  # Será calculado
                valor_final=0
            )
            
            # Adiciona produtos à venda
            valor_total = 0
            for produto_id, quantidade in zip(produtos_ids, quantidades):
                if produto_id and quantidade:
                    produto = Produto.objects.get(id=produto_id, loja=loja)
                    quantidade = int(quantidade)
                    
                    # Cria item da venda
                    ItemVenda.objects.create(
                        venda=venda,
                        produto=produto,
                        quantidade=quantidade,
                        preco_unitario=produto.preco
                    )
                    
                    valor_total += produto.preco * quantidade
            
            # Atualiza valores da venda
            venda.valor_total = valor_total
            venda.valor_final = valor_total
            venda.save()
            
            messages.success(request, f'Venda {venda.numero_venda} criada com sucesso!')
            return redirect('detalhar_venda', venda_id=venda.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar venda: {str(e)}')
    
    # Busca clientes e produtos da loja
    clientes = Cliente.objects.filter(loja=loja, ativo=True)
    produtos = Produto.objects.filter(loja=loja, ativo=True)
    
    context = {
        'loja': loja,
        'clientes': clientes,
        'produtos': produtos,
    }
    
    return render(request, 'lojas/nova_venda.html', context)


@login_required
def detalhar_venda(request, venda_id):
    """Detalha uma venda específica"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    venda = get_object_or_404(Venda, id=venda_id, loja=loja)
    itens = ItemVenda.objects.filter(venda=venda)
    
    context = {
        'venda': venda,
        'itens': itens,
        'loja': loja,
    }
    
    return render(request, 'lojas/detalhar_venda.html', context)


@login_required
def gerenciar_cardapio(request):
    """Gerencia o cardápio da lanchonete"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    # Verificar se é uma lanchonete
    if not loja.tipo_loja or loja.tipo_loja.nome != 'lanchonete':
        messages.error(request, 'Esta funcionalidade é apenas para lanchonetes.')
        return redirect('dashboard:loja')
    
    # Buscar itens do cardápio (produtos da loja)
    cardapio = Produto.objects.filter(loja=loja).order_by('categoria', 'nome')
    
    # Filtros
    search = request.GET.get('search')
    if search:
        cardapio = cardapio.filter(
            Q(nome__icontains=search) |
            Q(descricao__icontains=search)
        )
    
    categoria_filter = request.GET.get('categoria')
    if categoria_filter:
        cardapio = cardapio.filter(categoria=categoria_filter)
    
    ativo_filter = request.GET.get('ativo')
    if ativo_filter is not None:
        cardapio = cardapio.filter(ativo=ativo_filter == 'true')
    
    # Categorias para lanchonetes
    categorias_cardapio = [
        ('lanches', 'Lanches'),
        ('bebidas', 'Bebidas'),
        ('sobremesas', 'Sobremesas'),
        ('porcoes', 'Porções'),
        ('combos', 'Combos'),
        ('outros', 'Outros'),
    ]
    
    context = {
        'cardapio': cardapio,
        'loja': loja,
        'search': search,
        'categoria_filter': categoria_filter,
        'ativo_filter': ativo_filter,
        'categorias_cardapio': categorias_cardapio,
    }
    
    return render(request, 'lojas/cardapio.html', context)


@login_required
def adicionar_item_cardapio(request):
    """Adiciona um novo item ao cardápio"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    # Verificar se é uma lanchonete
    if not loja.tipo_loja or loja.tipo_loja.nome != 'lanchonete':
        messages.error(request, 'Esta funcionalidade é apenas para lanchonetes.')
        return redirect('dashboard:loja')
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        
        if form.is_valid():
            produto = form.save(commit=False)
            produto.loja = loja
            produto.save()
            
            messages.success(request, f'Item "{produto.nome}" adicionado ao cardápio com sucesso!')
            return redirect('lojas:gerenciar_cardapio')
    else:
        form = ProdutoForm()
    
    # Categorias específicas para lanchonetes
    categorias_cardapio = [
        ('lanches', 'Lanches'),
        ('bebidas', 'Bebidas'),
        ('sobremesas', 'Sobremesas'),
        ('porcoes', 'Porções'),
        ('combos', 'Combos'),
        ('outros', 'Outros'),
    ]
    
    context = {
        'form': form,
        'loja': loja,
        'categorias_cardapio': categorias_cardapio,
    }
    
    return render(request, 'lojas/adicionar_item_cardapio.html', context)


@login_required
def editar_item_cardapio(request, produto_id):
    """Edita um item do cardápio"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    produto = get_object_or_404(Produto, id=produto_id, loja=loja)
    
    # Verificar se é uma lanchonete
    if not loja.tipo_loja or loja.tipo_loja.nome != 'lanchonete':
        messages.error(request, 'Esta funcionalidade é apenas para lanchonetes.')
        return redirect('dashboard:loja')
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES, instance=produto)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Item "{produto.nome}" atualizado com sucesso!')
            return redirect('lojas:gerenciar_cardapio')
    else:
        form = ProdutoForm(instance=produto)
    
    # Categorias específicas para lanchonetes
    categorias_cardapio = [
        ('lanches', 'Lanches'),
        ('bebidas', 'Bebidas'),
        ('sobremesas', 'Sobremesas'),
        ('porcoes', 'Porções'),
        ('combos', 'Combos'),
        ('outros', 'Outros'),
    ]
    
    context = {
        'form': form,
        'produto': produto,
        'loja': loja,
        'categorias_cardapio': categorias_cardapio,
    }
    
    return render(request, 'lojas/editar_item_cardapio.html', context)


@login_required
def gerenciar_mesas(request):
    """Gerencia as mesas da lanchonete"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    # Verificar se é uma lanchonete
    if not loja.tipo_loja or loja.tipo_loja.nome != 'lanchonete':
        messages.error(request, 'Esta funcionalidade é apenas para lanchonetes.')
        return redirect('dashboard:loja')
    
    from .models import Mesa
    mesas = Mesa.objects.filter(loja=loja).order_by('numero')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        mesas = mesas.filter(status=status_filter)
    
    context = {
        'mesas': mesas,
        'loja': loja,
        'status_filter': status_filter,
    }
    
    return render(request, 'lojas/mesas.html', context)


@login_required
def adicionar_mesa(request):
    """Adiciona uma nova mesa"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    # Verificar se é uma lanchonete
    if not loja.tipo_loja or loja.tipo_loja.nome != 'lanchonete':
        messages.error(request, 'Esta funcionalidade é apenas para lanchonetes.')
        return redirect('dashboard:loja')
    
    if request.method == 'POST':
        from .models import Mesa
        
        numero = request.POST.get('numero')
        capacidade = request.POST.get('capacidade')
        localizacao = request.POST.get('localizacao', '')
        observacoes = request.POST.get('observacoes', '')
        
        try:
            mesa = Mesa.objects.create(
                loja=loja,
                numero=int(numero),
                capacidade=int(capacidade),
                localizacao=localizacao,
                observacoes=observacoes
            )
            
            messages.success(request, f'Mesa {mesa.numero} adicionada com sucesso!')
            return redirect('lojas:gerenciar_mesas')
            
        except Exception as e:
            messages.error(request, f'Erro ao adicionar mesa: {str(e)}')
    
    context = {
        'loja': loja,
    }
    
    return render(request, 'lojas/adicionar_mesa.html', context)


@login_required
def editar_mesa(request, mesa_id):
    """Edita uma mesa"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    from .models import Mesa
    mesa = get_object_or_404(Mesa, id=mesa_id, loja=loja)
    
    if request.method == 'POST':
        mesa.numero = int(request.POST.get('numero'))
        mesa.capacidade = int(request.POST.get('capacidade'))
        mesa.localizacao = request.POST.get('localizacao', '')
        mesa.observacoes = request.POST.get('observacoes', '')
        mesa.ativa = request.POST.get('ativa') == 'on'
        
        try:
            mesa.save()
            messages.success(request, f'Mesa {mesa.numero} atualizada com sucesso!')
            return redirect('lojas:gerenciar_mesas')
        except Exception as e:
            messages.error(request, f'Erro ao atualizar mesa: {str(e)}')
    
    context = {
        'mesa': mesa,
        'loja': loja,
    }
    
    return render(request, 'lojas/editar_mesa.html', context)


@login_required
def alterar_status_mesa(request, mesa_id):
    """Altera o status de uma mesa"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    from .models import Mesa
    mesa = get_object_or_404(Mesa, id=mesa_id, loja=loja)
    
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status in ['livre', 'ocupada', 'reservada', 'manutencao']:
            mesa.status = novo_status
            mesa.save()
            
            messages.success(request, f'Status da Mesa {mesa.numero} alterado para {mesa.get_status_display()}.')
    
    return redirect('lojas:gerenciar_mesas')


@login_required
def gerenciar_pedidos(request):
    """Gerencia os pedidos da lanchonete"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    # Verificar se é uma lanchonete
    if not loja.tipo_loja or loja.tipo_loja.nome != 'lanchonete':
        messages.error(request, 'Esta funcionalidade é apenas para lanchonetes.')
        return redirect('dashboard:loja')
    
    from .models import Pedido
    pedidos = Pedido.objects.filter(loja=loja).order_by('-data_pedido')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        pedidos = pedidos.filter(status=status_filter)
    
    tipo_filter = request.GET.get('tipo')
    if tipo_filter:
        pedidos = pedidos.filter(tipo=tipo_filter)
    
    context = {
        'pedidos': pedidos,
        'loja': loja,
        'status_filter': status_filter,
        'tipo_filter': tipo_filter,
    }
    
    return render(request, 'lojas/pedidos.html', context)


@login_required
def novo_pedido(request):
    """Cria um novo pedido"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    # Verificar se é uma lanchonete
    if not loja.tipo_loja or loja.tipo_loja.nome != 'lanchonete':
        messages.error(request, 'Esta funcionalidade é apenas para lanchonetes.')
        return redirect('dashboard:loja')
    
    from .models import Mesa, Pedido, ItemPedido
    
    # Buscar mesas livres e produtos do cardápio
    mesas_livres = Mesa.objects.filter(loja=loja, status='livre', ativa=True)
    cardapio = Produto.objects.filter(loja=loja, ativo=True)
    clientes = Cliente.objects.filter(loja=loja, ativo=True)
    
    if request.method == 'POST':
        try:
            # Dados do pedido
            tipo = request.POST.get('tipo')
            mesa_id = request.POST.get('mesa') if tipo == 'mesa' else None
            cliente_id = request.POST.get('cliente')
            observacoes = request.POST.get('observacoes', '')
            
            # Criar pedido
            pedido = Pedido.objects.create(
                loja=loja,
                tipo=tipo,
                mesa_id=mesa_id if mesa_id else None,
                cliente_id=cliente_id if cliente_id else None,
                observacoes=observacoes,
                valor_total=0
            )
            
            # Adicionar itens
            produtos_ids = request.POST.getlist('produtos')
            quantidades = request.POST.getlist('quantidades')
            
            valor_total = 0
            for produto_id, quantidade in zip(produtos_ids, quantidades):
                if produto_id and quantidade:
                    produto = Produto.objects.get(id=produto_id, loja=loja)
                    quantidade = int(quantidade)
                    
                    ItemPedido.objects.create(
                        pedido=pedido,
                        produto=produto,
                        quantidade=quantidade,
                        preco_unitario=produto.preco
                    )
                    
                    valor_total += produto.preco * quantidade
            
            # Atualizar valor do pedido
            pedido.valor_total = valor_total
            pedido.valor_final = valor_total
            pedido.save()
            
            # Se for mesa, ocupar a mesa
            if mesa_id:
                mesa = Mesa.objects.get(id=mesa_id)
                mesa.status = 'ocupada'
                mesa.save()
            
            messages.success(request, f'Pedido {pedido.numero_pedido} criado com sucesso!')
            return redirect('lojas:detalhar_pedido', pedido_id=pedido.id)
            
        except Exception as e:
            messages.error(request, f'Erro ao criar pedido: {str(e)}')
    
    context = {
        'loja': loja,
        'mesas_livres': mesas_livres,
        'cardapio': cardapio,
        'clientes': clientes,
    }
    
    return render(request, 'lojas/novo_pedido.html', context)


@login_required
def detalhar_pedido(request, pedido_id):
    """Detalha um pedido específico"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    from .models import Pedido, ItemPedido
    pedido = get_object_or_404(Pedido, id=pedido_id, loja=loja)
    itens = ItemPedido.objects.filter(pedido=pedido)
    
    context = {
        'pedido': pedido,
        'itens': itens,
        'loja': loja,
    }
    
    return render(request, 'lojas/detalhar_pedido.html', context)


@login_required
def alterar_status_pedido(request, pedido_id):
    """Altera o status de um pedido"""
    
    if not hasattr(request, 'loja_atual'):
        messages.error(request, 'Você não tem uma loja associada.')
        return redirect('dashboard:principal')
    
    loja = request.loja_atual
    
    from .models import Pedido
    pedido = get_object_or_404(Pedido, id=pedido_id, loja=loja)
    
    if request.method == 'POST':
        novo_status = request.POST.get('status')
        if novo_status in ['pendente', 'preparando', 'pronto', 'entregue', 'cancelado']:
            pedido.status = novo_status
            
            # Se entregue, liberar mesa
            if novo_status == 'entregue' and pedido.mesa:
                pedido.mesa.status = 'livre'
                pedido.mesa.save()
                pedido.data_entrega = timezone.now()
            
            pedido.save()
            
            messages.success(request, f'Status do Pedido {pedido.numero_pedido} alterado para {pedido.get_status_display()}.')
    
    return redirect('lojas:detalhar_pedido', pedido_id=pedido.id)


@login_required
@user_passes_test(is_superuser)
def acessar_login_personalizado(request, loja_id):
    """Redireciona para o login personalizado da loja"""
    
    loja = get_object_or_404(Loja, id=loja_id)
    
    try:
        # Buscar configuração de login personalizado
        from .models_login import LoginPersonalizado
        login_config = LoginPersonalizado.objects.get(loja=loja, ativo=True)
        
        # Redirecionar para o login personalizado
        return redirect(login_config.get_login_url())
        
    except LoginPersonalizado.DoesNotExist:
        # Se não existe login personalizado, criar um
        try:
            from .signals import criar_login_personalizado
            login_config = criar_login_personalizado(loja)
            
            messages.success(request, f'Login personalizado criado para {loja.nome}!')
            return redirect(login_config.get_login_url())
            
        except Exception as e:
            messages.error(request, f'Erro ao criar login personalizado: {str(e)}')
            return redirect('lojas:detalhar_loja', loja_id=loja.id)
    
    except Exception as e:
        messages.error(request, f'Erro ao acessar login da loja: {str(e)}')
        return redirect('lojas:detalhar_loja', loja_id=loja.id)


@login_required
@user_passes_test(is_superuser)
def enviar_credenciais_provisorias(request, loja_id):
    """Envia novas credenciais provisórias para o administrador da loja"""
    
    loja = get_object_or_404(Loja, id=loja_id)
    
    if request.method == 'POST':
        # Verificar se não foi enviado recentemente (proteção contra duplo clique)
        from django.utils import timezone
        from datetime import timedelta
        
        # Verificar se há um envio recente (últimos 30 segundos)
        cache_key = f"credenciais_enviadas_{loja.id}_{request.user.id}"
        from django.core.cache import cache
        
        if cache.get(cache_key):
            messages.warning(request, 'Credenciais já foram enviadas recentemente. Aguarde alguns segundos antes de tentar novamente.')
            return redirect('lojas:detalhar_loja', loja_id=loja.id)
        
        # Marcar como enviado por 30 segundos
        cache.set(cache_key, True, 30)
        try:
            from django.db import transaction
            from django.utils import timezone
            from django.core.mail import send_mail
            from django.conf import settings
            import secrets
            import string
            
            with transaction.atomic():
                # Gerar nova senha provisória
                password_chars = string.ascii_letters + string.digits + "!@#$%&*"
                nova_senha_provisoria = ''.join(secrets.choice(password_chars) for _ in range(12))
                
                # Atualizar senha do usuário administrador da loja
                admin_user = loja.admin_user
                admin_user.set_password(nova_senha_provisoria)
                admin_user.save()
                
                # Atualizar senha provisória na loja
                loja.senha_provisoria = nova_senha_provisoria
                loja.save()
                
                # Atualizar perfil do usuário para marcar troca obrigatória
                try:
                    from usuarios.models import PerfilUsuario
                    profile, created = PerfilUsuario.objects.get_or_create(
                        user=admin_user,
                        defaults={
                            'is_super_admin': False,
                            'requires_password_change': True,
                            'provisional_password_created': timezone.now(),
                            'password_change_reminders_sent': 0
                        }
                    )
                    
                    if not created:
                        profile.requires_password_change = True
                        profile.provisional_password_created = timezone.now()
                        profile.password_change_reminders_sent = 0
                        profile.save()
                        
                except Exception as profile_error:
                    # Continua mesmo se houver erro no perfil
                    logger.warning(f'Erro ao atualizar perfil do usuário {admin_user.username}: {str(profile_error)}')
                
                # Enviar email com novas credenciais
                email_sent = False
                try:
                    subject = f'Novas Credenciais de Acesso - {loja.nome}'
                    message = f"""Olá {admin_user.first_name or loja.nome},

Suas credenciais de acesso foram atualizadas para a loja: {loja.nome}

🏪 DADOS DA LOJA:
Nome: {loja.nome}
CNPJ: {loja.cnpj}
Email: {loja.email}
Telefone: {loja.telefone}

🔑 CREDENCIAIS DE ACESSO:
URL de Login: https://www.lvksistemas.com.br/loja/login/
Usuário: {loja.email}
Nova Senha Provisória: {nova_senha_provisoria}

⚠️ INSTRUÇÕES IMPORTANTES:
1. Acesse o link: https://www.lvksistemas.com.br/loja/login/
2. Use o EMAIL DA LOJA como usuário: {loja.email}
3. Use a senha provisória fornecida acima
4. Você será obrigado a alterar a senha no primeiro acesso
5. Mantenha suas credenciais em local seguro

📧 Esta senha provisória foi gerada por solicitação do administrador do sistema.

Em caso de dúvidas, entre em contato conosco:
📞 Suporte: suporte@lvksistemas.com.br

Atenciosamente,
Equipe LVK Sistemas"""
                    
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [loja.email],
                        fail_silently=False,
                    )
                    email_sent = True
                    
                except Exception as email_error:
                    logger.error(f'Erro ao enviar email para {loja.email}: {str(email_error)}')
                
                # Log da operação
                logger.info(f'Novas credenciais provisórias geradas para loja "{loja.nome}" por {request.user.username}')
                logger.info(f'Email enviado para: {loja.email} | Senha: {nova_senha_provisoria}')
                
                # Criar notificação
                try:
                    from dashboard.models import Notificacao
                    Notificacao.objects.create(
                        titulo=f"Credenciais enviadas - {loja.nome}",
                        mensagem=f"Novas credenciais provisórias foram geradas e enviadas para {loja.email}",
                        tipo='success',
                        prioridade='alta',
                        usuario=request.user,
                        loja=loja
                    )
                except:
                    pass  # Ignora erro se não conseguir criar notificação
            
            # Mensagem de sucesso
            if email_sent:
                messages.success(request, 
                    f'✅ Novas credenciais provisórias geradas com sucesso!\n'
                    f'📧 Email enviado para: {loja.email}\n'
                    f'🔑 Nova senha: {nova_senha_provisoria}\n'
                    f'⚠️ O administrador deve trocar a senha no primeiro acesso.')
            else:
                messages.warning(request, 
                    f'⚠️ Novas credenciais geradas, mas houve problema no envio do email.\n'
                    f'🔑 Nova senha provisória: {nova_senha_provisoria}\n'
                    f'📧 Informe manualmente ao administrador: {loja.email}')
            
            return redirect('lojas:detalhar_loja', loja_id=loja.id)
            
        except Exception as e:
            logger.error(f'Erro ao gerar credenciais provisórias para loja "{loja.nome}": {str(e)}')
            messages.error(request, f'❌ Erro ao gerar novas credenciais: {str(e)}')
            return redirect('lojas:detalhar_loja', loja_id=loja.id)
    
    # Se não for POST, redireciona para detalhes da loja
    return redirect('lojas:detalhar_loja', loja_id=loja.id)
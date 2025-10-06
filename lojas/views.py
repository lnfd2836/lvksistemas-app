from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import Loja, Cliente, Produto, Venda, BackupLoja
from .forms import LojaForm, ClienteForm, ProdutoForm
from dashboard.models import Notificacao
from controle_financeiro.models import ControleFinanceiro, PlanoFinanceiro, ConfiguracaoBoleto, BoletoGerado
from datetime import timedelta


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
    
    lojas = Loja.objects.all().order_by('-data_criacao')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        lojas = lojas.filter(status=status_filter)
    
    tipo_filter = request.GET.get('tipo_loja')
    if tipo_filter:
        lojas = lojas.filter(tipo_loja__nome=tipo_filter)
    
    search = request.GET.get('search')
    if search:
        lojas = lojas.filter(
            Q(nome__icontains=search) |
            Q(cnpj__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Estatísticas por tipo de loja
    stats_tipos = {}
    for tipo in ['conveniencia', 'roupas', 'tintas', 'supermercado', 'lanchonete']:
        stats_tipos[tipo] = Loja.objects.filter(tipo_loja__nome=tipo).count()
    
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
    
    if request.method == 'POST':
        form = LojaForm(request.POST)
        
        if form.is_valid():
            with transaction.atomic():
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
                
                # Cria a loja
                loja = form.save(commit=False)
                loja.admin_user = admin_user
                loja.save()
                
                # Define a senha do usuário administrador
                admin_user.set_password(loja.senha_provisoria)
                admin_user.save()
                
                # Cria controle financeiro automaticamente
                try:
                    # Busca o plano básico (primeiro plano ativo)
                    plano_basico = PlanoFinanceiro.objects.filter(ativo=True).first()
                    if not plano_basico:
                        # Cria um plano básico se não existir
                        plano_basico = PlanoFinanceiro.objects.create(
                            nome="Básico",
                            descricao="Plano básico para novas lojas",
                            valor_mensal=29.90,
                            dias_trial=30,
                            ativo=True
                        )
                    
                    # Cria o controle financeiro
                    controle_financeiro = ControleFinanceiro.objects.create(
                        loja=loja,
                        plano=plano_basico,
                        status='ativa',
                        valor_mensal=plano_basico.valor_mensal,
                        data_inicio=timezone.now(),
                        data_vencimento=timezone.now() + timedelta(days=plano_basico.dias_trial)
                    )
                    
                    # Gera boleto automaticamente usando a configuração padrão
                    configuracao_boleto = ConfiguracaoBoleto.objects.filter(ativo=True).first()
                    if configuracao_boleto:
                        # Gera número do boleto
                        numero_boleto = f"BOL{timezone.now().strftime('%Y%m%d%H%M%S')}"
                        linha_digitavel = f"23791{configuracao_boleto.agencia.zfill(4)}{configuracao_boleto.conta.zfill(8)}{numero_boleto.zfill(10)}"
                        codigo_barras = linha_digitavel.replace(' ', '')
                        
                        # Cria o boleto
                        boleto = BoletoGerado.objects.create(
                            controle_financeiro=controle_financeiro,
                            configuracao=configuracao_boleto,
                            numero_boleto=numero_boleto,
                            linha_digitavel=linha_digitavel,
                            codigo_barras=codigo_barras,
                            valor=plano_basico.valor_mensal,
                            data_vencimento=timezone.now() + timedelta(days=7),
                            status='pendente'
                        )
                        
                        # Cria notificação sobre o boleto
                        try:
                            Notificacao.objects.create(
                                titulo=f"Boleto gerado para {loja.nome}",
                                mensagem=f"Boleto {numero_boleto} gerado automaticamente. Valor: R$ {plano_basico.valor_mensal}",
                                tipo='info',
                                prioridade='media',
                                usuario=request.user
                            )
                        except:
                            pass
                    
                except Exception as e:
                    # Log do erro mas não impede a criação da loja
                    print(f"Erro ao criar controle financeiro: {str(e)}")
                
                # Cria notificação de sucesso
                try:
                    Notificacao.objects.create(
                        titulo=f"Loja {loja.nome} criada com sucesso",
                        mensagem=f"A loja {loja.nome} foi criada com sucesso. Controle financeiro e boleto gerados automaticamente.",
                        tipo='success',
                        prioridade='media',
                        usuario=request.user
                    )
                except:
                    pass  # Ignora erro se não conseguir criar notificação
                
                # Envia email com senha provisória
                try:
                    send_mail(
                        f'Conta criada para {loja.nome}',
                        f'''
                        Sua conta foi criada com sucesso!
                        
                        Loja: {loja.nome}
                        Email: {loja.email}
                        Senha Provisória: {loja.senha_provisoria}
                        
                        IMPORTANTE: Altere sua senha no primeiro acesso.
                        ''',
                        settings.EMAIL_HOST_USER,
                        [loja.email],
                        fail_silently=False,
                    )
                    
                    messages.success(request, f'Loja {loja.nome} criada com sucesso! Email enviado com senha provisória.')
                except Exception as e:
                    messages.success(request, f'Loja {loja.nome} criada com sucesso! Senha provisória: {loja.senha_provisoria}')
                
                return redirect('lojas:listar_lojas')
    else:
        form = LojaForm()
    
    return render(request, 'lojas/criar.html', {'form': form})


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
    
    loja = get_object_or_404(Loja, id=loja_id)
    
    # Estatísticas da loja
    total_clientes = Cliente.objects.filter(loja=loja).count()
    total_produtos = Produto.objects.filter(loja=loja).count()
    total_vendas = Venda.objects.filter(loja=loja).count()
    
    # Vendas recentes
    vendas_recentes = Venda.objects.filter(loja=loja).order_by('-data_venda')[:10]
    
    # Backups da loja
    backups = BackupLoja.objects.filter(loja=loja).order_by('-data_backup')[:5]
    
    # Informações do plano comercial
    try:
        from planos.models import AssinaturaLoja
        assinatura = AssinaturaLoja.objects.get(loja=loja, status='ativa')
        plano = assinatura.plano
        dias_vencimento = assinatura.dias_para_vencimento()
        limites_atingidos = assinatura.verificar_limites()
    except:
        assinatura = None
        plano = None
        dias_vencimento = 0
        limites_atingidos = {}
    
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
    
    context = {
        'clientes': clientes,
        'loja': loja,
        'search': search,
        'ativo_filter': ativo_filter,
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
    
    context = {
        'produtos': produtos,
        'loja': loja,
        'search': search,
        'categoria_filter': categoria_filter,
        'ativo_filter': ativo_filter,
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
    
    return redirect('detalhar_loja', loja_id=loja_id)

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
                
                # 6. Exclui usuário administrador
                if admin_user:
                    admin_user.delete()
                
                # 7. Exclui a loja
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
                
        except Exception as e:
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
    
    context = {
        'vendas': vendas,
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


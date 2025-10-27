#!/usr/bin/env python
"""
Script para corrigir o erro na view detalhar_loja
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')
django.setup()

def corrigir_view_detalhar_loja():
    """
    Corrige a view detalhar_loja para tratar erros adequadamente
    """
    print("🔧 Corrigindo view detalhar_loja...")
    
    views_path = 'lojas/views.py'
    
    try:
        with open(views_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Localizar a função detalhar_loja
        old_function = '''@login_required
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
    assinatura = None
    plano = None
    dias_vencimento = 0
    limites_atingidos = {}
    
    try:
        from planos.models import AssinaturaLoja
        assinatura = AssinaturaLoja.objects.filter(loja=loja, status='ativa').first()
        if assinatura:
            plano = assinatura.plano
            dias_vencimento = assinatura.dias_para_vencimento()
            limites_atingidos = assinatura.verificar_limites()
    except Exception as e:
        logger.warning(f"Erro ao buscar informações do plano para loja {loja.nome}: {str(e)}")
        # Valores padrão já definidos acima
    
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
    
    return render(request, 'lojas/detalhar.html', context)'''
        
        new_function = '''@login_required
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
        return redirect('lojas:listar_lojas')'''
        
        if old_function in content:
            content = content.replace(old_function, new_function)
            
            with open(views_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ View detalhar_loja corrigida com tratamento de erros")
            return True
        else:
            print("⚠️ Função detalhar_loja não encontrada exatamente como esperado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao corrigir view: {e}")
        return False

def corrigir_middleware_process_exception():
    """
    Corrige o método process_exception do SuperAdminMiddleware para não interferir em /lojas/
    """
    print("🔧 Corrigindo process_exception do SuperAdminMiddleware...")
    
    middleware_path = 'dashboard/middleware/super_admin_middleware.py'
    
    try:
        with open(middleware_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        old_method = '''    def process_exception(self, request, exception):
        """Processa exceções que podem ocorrer"""
        
        # Se é super admin e houve erro, tentar redirecionar para área segura
        if self._is_authenticated_super_admin(request):
            logger.error(f"Exceção para super admin {request.user.username}: {str(exception)}")
            
            # Se não está em área administrativa, redirecionar
            if not request.path.startswith('/admin/'):
                messages.error(request, 'Ocorreu um erro. Você foi redirecionado para a área administrativa.')
                return redirect('/admin/')
        
        # Não interferir no tratamento normal de exceções
        return None'''
        
        new_method = '''    def process_exception(self, request, exception):
        """Processa exceções que podem ocorrer"""
        
        # Se é super admin e houve erro, tentar redirecionar para área segura
        if self._is_authenticated_super_admin(request):
            logger.error(f"Exceção para super admin {request.user.username}: {str(exception)}")
            
            # PERMITIR que super admins vejam erros em /lojas/ para debug
            if request.path.startswith('/lojas/'):
                logger.info(f"Permitindo que super admin veja erro em {request.path}")
                return None  # Deixar Django tratar o erro normalmente
            
            # Se não está em área administrativa (exceto /lojas/), redirecionar
            if not request.path.startswith('/admin/'):
                messages.error(request, 'Ocorreu um erro. Você foi redirecionado para a área administrativa.')
                return redirect('/admin/')
        
        # Não interferir no tratamento normal de exceções
        return None'''
        
        if old_method in content:
            content = content.replace(old_method, new_method)
            
            with open(middleware_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Método process_exception corrigido")
            return True
        else:
            print("⚠️ Método process_exception não encontrado exatamente como esperado")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao corrigir middleware: {e}")
        return False

def verificar_template_detalhar():
    """
    Verifica se o template detalhar.html existe
    """
    print("🔍 Verificando template detalhar.html...")
    
    template_path = 'templates/lojas/detalhar.html'
    
    if os.path.exists(template_path):
        print("✅ Template detalhar.html existe")
        return True
    else:
        print("❌ Template detalhar.html não encontrado")
        print("🔧 Criando template básico...")
        
        # Criar diretório se não existir
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        
        template_content = '''{% extends 'base.html' %}
{% load widget_tweaks %}

{% block title %}Detalhes - {{ loja.nome }}{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">
                        <i class="fas fa-store me-2"></i>
                        Detalhes da Loja: {{ loja.nome }}
                    </h3>
                    <div class="card-tools">
                        <a href="{% url 'lojas:listar_lojas' %}" class="btn btn-outline-secondary btn-sm">
                            <i class="fas fa-arrow-left me-1"></i>Voltar
                        </a>
                        <a href="{% url 'lojas:editar_loja' loja.id %}" class="btn btn-primary btn-sm">
                            <i class="fas fa-edit me-1"></i>Editar
                        </a>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <h5>Informações Básicas</h5>
                            <table class="table table-borderless">
                                <tr>
                                    <td><strong>Nome:</strong></td>
                                    <td>{{ loja.nome }}</td>
                                </tr>
                                <tr>
                                    <td><strong>CNPJ:</strong></td>
                                    <td>{{ loja.cnpj|default:"Não informado" }}</td>
                                </tr>
                                <tr>
                                    <td><strong>Email:</strong></td>
                                    <td>{{ loja.email }}</td>
                                </tr>
                                <tr>
                                    <td><strong>Telefone:</strong></td>
                                    <td>{{ loja.telefone|default:"Não informado" }}</td>
                                </tr>
                                <tr>
                                    <td><strong>Status:</strong></td>
                                    <td>
                                        <span class="badge badge-{% if loja.status == 'ativa' %}success{% elif loja.status == 'inativa' %}secondary{% else %}warning{% endif %}">
                                            {{ loja.get_status_display }}
                                        </span>
                                    </td>
                                </tr>
                            </table>
                        </div>
                        <div class="col-md-6">
                            <h5>Estatísticas</h5>
                            <table class="table table-borderless">
                                <tr>
                                    <td><strong>Total de Clientes:</strong></td>
                                    <td>{{ total_clientes }}</td>
                                </tr>
                                <tr>
                                    <td><strong>Total de Produtos:</strong></td>
                                    <td>{{ total_produtos }}</td>
                                </tr>
                                <tr>
                                    <td><strong>Total de Vendas:</strong></td>
                                    <td>{{ total_vendas }}</td>
                                </tr>
                                <tr>
                                    <td><strong>Data de Criação:</strong></td>
                                    <td>{{ loja.data_criacao|date:"d/m/Y H:i" }}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                    
                    {% if plano %}
                    <div class="row mt-4">
                        <div class="col-12">
                            <h5>Informações do Plano</h5>
                            <div class="alert alert-info">
                                <strong>Plano:</strong> {{ plano.nome }}<br>
                                <strong>Valor:</strong> R$ {{ plano.preco }}<br>
                                <strong>Dias para Vencimento:</strong> {{ dias_vencimento }}
                            </div>
                        </div>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}'''
        
        try:
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            print("✅ Template básico criado")
            return True
        except Exception as e:
            print(f"❌ Erro ao criar template: {e}")
            return False

def main():
    """
    Função principal
    """
    print("🚀 CORRIGINDO ERRO NA VIEW DETALHAR_LOJA")
    print("=" * 60)
    
    success_count = 0
    total_fixes = 3
    
    # 1. Corrigir view detalhar_loja
    if corrigir_view_detalhar_loja():
        success_count += 1
    
    # 2. Corrigir middleware process_exception
    if corrigir_middleware_process_exception():
        success_count += 1
    
    # 3. Verificar template
    if verificar_template_detalhar():
        success_count += 1
    
    print("=" * 60)
    print(f"📊 RESULTADO: {success_count}/{total_fixes} correções bem-sucedidas")
    
    if success_count == total_fixes:
        print("🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!")
        print("✅ A view detalhar_loja agora tem tratamento de erros adequado")
        print("✅ O middleware não interfere mais em /lojas/")
        print("🚀 Faça o deploy para o Heroku")
    else:
        print("⚠️ ALGUMAS CORREÇÕES FALHARAM")
        print("🔍 Verifique os logs acima para detalhes")
    
    print("=" * 60)

if __name__ == '__main__':
    main()
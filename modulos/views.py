from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import TipoLoja, ModuloLoja, CampoPersonalizado
from .forms import TipoLojaForm


def is_superuser(user):
    """Verifica se o usuário é super usuário"""
    return user.is_superuser


@login_required
@user_passes_test(is_superuser)
def listar_tipos_loja(request):
    """Lista todos os tipos de loja"""
    tipos_loja = TipoLoja.objects.all().order_by('nome')
    
    context = {
        'tipos_loja': tipos_loja,
    }
    
    return render(request, 'modulos/listar_tipos_loja.html', context)


@login_required
@user_passes_test(is_superuser)
def editar_tipo_loja(request, tipo_id):
    """Edita um tipo de loja"""
    tipo_loja = get_object_or_404(TipoLoja, id=tipo_id)
    
    if request.method == 'POST':
        form = TipoLojaForm(request.POST, instance=tipo_loja)
        if form.is_valid():
            form.save()
            messages.success(request, f'Tipo de loja "{tipo_loja.nome}" atualizado com sucesso!')
            return redirect('modulos:listar_tipos_loja')
    else:
        form = TipoLojaForm(instance=tipo_loja)
    
    # Buscar módulos e campos personalizados relacionados
    modulos = ModuloLoja.objects.filter(tipo_loja=tipo_loja).order_by('ordem')
    campos_personalizados = CampoPersonalizado.objects.filter(tipo_loja=tipo_loja).order_by('ordem')
    
    context = {
        'tipo_loja': tipo_loja,
        'form': form,
        'modulos': modulos,
        'campos_personalizados': campos_personalizados,
    }
    
    return render(request, 'modulos/editar_tipo_loja.html', context)


@login_required
@user_passes_test(is_superuser)
def criar_tipo_loja(request):
    """Cria um novo tipo de loja"""
    if request.method == 'POST':
        form = TipoLojaForm(request.POST)
        if form.is_valid():
            tipo_loja = form.save()
            messages.success(request, f'Tipo de loja "{tipo_loja.nome}" criado com sucesso!')
            return redirect('modulos:listar_tipos_loja')
    else:
        form = TipoLojaForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'modulos/criar_tipo_loja.html', context)


@login_required
@user_passes_test(is_superuser)
def excluir_tipo_loja(request, tipo_id):
    """Exclui um tipo de loja"""
    tipo_loja = get_object_or_404(TipoLoja, id=tipo_id)
    
    if request.method == 'POST':
        nome = tipo_loja.nome
        tipo_loja.delete()
        messages.success(request, f'Tipo de loja "{nome}" excluído com sucesso!')
        return redirect('modulos:listar_tipos_loja')
    
    context = {
        'tipo_loja': tipo_loja,
    }
    
    return render(request, 'modulos/excluir_tipo_loja.html', context)

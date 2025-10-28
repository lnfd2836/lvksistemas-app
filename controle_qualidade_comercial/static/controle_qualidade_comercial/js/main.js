// Controle de Qualidade Comercial - JavaScript Principal

$(document).ready(function() {
    // Inicializar componentes
    initializeComponents();
    
    // Configurar CSRF Token para AJAX
    setupCSRF();
    
    // Configurar tooltips
    initializeTooltips();
    
    // Configurar máscaras de input
    initializeMasks();
    
    // Auto-save em formulários
    initializeAutoSave();
});

// Inicializar componentes gerais
function initializeComponents() {
    // Fade in para cards
    $('.card').addClass('fade-in');
    
    // Auto-hide para alertas
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Confirmar ações de exclusão
    $('.btn-delete').on('click', function(e) {
        e.preventDefault();
        const url = $(this).attr('href');
        const item = $(this).data('item') || 'este item';
        
        if (confirm(`Tem certeza que deseja excluir ${item}?`)) {
            window.location.href = url;
        }
    });
}

// Configurar CSRF Token para requisições AJAX
function setupCSRF() {
    const csrftoken = $('[name=csrfmiddlewaretoken]').val();
    
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// Inicializar tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Inicializar máscaras de input
function initializeMasks() {
    // Máscara para CPF
    $('input[name="cliente_cpf"], input[name="cpf"]').mask('000.000.000-00');
    
    // Máscara para CNPJ
    $('input[name="cnpj"]').mask('00.000.000/0000-00');
    
    // Máscara para telefone
    $('input[name*="telefone"]').mask('(00) 00000-0000');
    
    // Máscara para CEP
    $('input[name="cep"]').mask('00000-000');
    
    // Formatação de moeda
    $('input[name*="preco"], input[name*="valor"]').mask('#.##0,00', {
        reverse: true,
        translation: {
            '#': {pattern: /[0-9]/}
        }
    });
}

// Auto-save em formulários
function initializeAutoSave() {
    let autoSaveTimeout;
    
    $('form[data-autosave="true"] input, form[data-autosave="true"] textarea, form[data-autosave="true"] select').on('change', function() {
        clearTimeout(autoSaveTimeout);
        autoSaveTimeout = setTimeout(function() {
            saveFormData();
        }, 2000);
    });
}

// Salvar dados do formulário no localStorage
function saveFormData() {
    const form = $('form[data-autosave="true"]');
    if (form.length) {
        const formData = form.serialize();
        const formId = form.attr('id') || 'autosave-form';
        localStorage.setItem(`autosave-${formId}`, formData);
        
        showNotification('Dados salvos automaticamente', 'success', 2000);
    }
}

// Restaurar dados do formulário do localStorage
function restoreFormData() {
    const form = $('form[data-autosave="true"]');
    if (form.length) {
        const formId = form.attr('id') || 'autosave-form';
        const savedData = localStorage.getItem(`autosave-${formId}`);
        
        if (savedData) {
            // Implementar restauração de dados
            showNotification('Dados anteriores restaurados', 'info', 3000);
        }
    }
}

// Sistema de notificações
function showNotification(message, type = 'info', duration = 3000) {
    const alertClass = `alert-${type}`;
    const notification = $(`
        <div class="alert ${alertClass} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('body').append(notification);
    
    setTimeout(function() {
        notification.fadeOut('slow', function() {
            $(this).remove();
        });
    }, duration);
}

// Busca com autocomplete
function initializeAutocomplete(inputSelector, apiUrl, displayField = 'nome') {
    $(inputSelector).on('input', function() {
        const query = $(this).val();
        const input = $(this);
        
        if (query.length < 2) {
            hideAutocompleteResults(input);
            return;
        }
        
        $.get(apiUrl, { q: query })
            .done(function(data) {
                showAutocompleteResults(input, data, displayField);
            })
            .fail(function() {
                hideAutocompleteResults(input);
            });
    });
}

function showAutocompleteResults(input, results, displayField) {
    hideAutocompleteResults(input);
    
    if (results.length === 0) return;
    
    const dropdown = $('<div class="autocomplete-dropdown list-group position-absolute" style="z-index: 1000; width: 100%;"></div>');
    
    results.forEach(function(item) {
        const option = $(`
            <a href="#" class="list-group-item list-group-item-action" data-value="${item.id}">
                ${item[displayField]}
            </a>
        `);
        
        option.on('click', function(e) {
            e.preventDefault();
            input.val(item[displayField]);
            input.data('selected-id', item.id);
            hideAutocompleteResults(input);
        });
        
        dropdown.append(option);
    });
    
    input.parent().css('position', 'relative').append(dropdown);
}

function hideAutocompleteResults(input) {
    input.parent().find('.autocomplete-dropdown').remove();
}

// Validação de formulários
function validateForm(formSelector) {
    const form = $(formSelector);
    let isValid = true;
    
    // Limpar erros anteriores
    form.find('.is-invalid').removeClass('is-invalid');
    form.find('.invalid-feedback').remove();
    
    // Validar campos obrigatórios
    form.find('[required]').each(function() {
        const field = $(this);
        if (!field.val().trim()) {
            showFieldError(field, 'Este campo é obrigatório');
            isValid = false;
        }
    });
    
    // Validar emails
    form.find('input[type="email"]').each(function() {
        const field = $(this);
        const email = field.val().trim();
        if (email && !isValidEmail(email)) {
            showFieldError(field, 'Email inválido');
            isValid = false;
        }
    });
    
    // Validar números
    form.find('input[type="number"]').each(function() {
        const field = $(this);
        const value = field.val();
        const min = field.attr('min');
        const max = field.attr('max');
        
        if (value && min && parseFloat(value) < parseFloat(min)) {
            showFieldError(field, `Valor mínimo: ${min}`);
            isValid = false;
        }
        
        if (value && max && parseFloat(value) > parseFloat(max)) {
            showFieldError(field, `Valor máximo: ${max}`);
            isValid = false;
        }
    });
    
    return isValid;
}

function showFieldError(field, message) {
    field.addClass('is-invalid');
    field.after(`<div class="invalid-feedback">${message}</div>`);
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Formatação de números
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

function formatNumber(value, decimals = 2) {
    return new Intl.NumberFormat('pt-BR', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    }).format(value);
}

// Utilitários para datas
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('pt-BR');
}

// Loading states
function showLoading(element) {
    const spinner = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>';
    element.prop('disabled', true).prepend(spinner);
}

function hideLoading(element) {
    element.prop('disabled', false).find('.spinner-border').remove();
}

// Exportar dados
function exportData(type, format = 'csv') {
    const url = `/exportar/${type}/?format=${format}`;
    window.open(url, '_blank');
}

// Imprimir página
function printPage() {
    window.print();
}

// Confirmar ação
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Atualizar progresso de meta
function updateMetaProgress(metaId, novoValor) {
    $.post(`/metas/${metaId}/atualizar-progresso/`, {
        valor_atual: novoValor
    })
    .done(function(data) {
        if (data.success) {
            showNotification('Progresso atualizado com sucesso!', 'success');
            // Atualizar interface
            updateProgressBar(metaId, data.percentual_atingido);
        } else {
            showNotification('Erro ao atualizar progresso', 'danger');
        }
    })
    .fail(function() {
        showNotification('Erro de conexão', 'danger');
    });
}

function updateProgressBar(metaId, percentual) {
    const progressBar = $(`#meta-${metaId} .progress-bar`);
    progressBar.css('width', `${percentual}%`).attr('aria-valuenow', percentual);
    progressBar.next('.progress-text').text(`${percentual}%`);
}

// Busca em tempo real
function initializeRealTimeSearch(inputSelector, tableSelector) {
    $(inputSelector).on('input', function() {
        const query = $(this).val().toLowerCase();
        const table = $(tableSelector);
        
        table.find('tbody tr').each(function() {
            const row = $(this);
            const text = row.text().toLowerCase();
            
            if (text.includes(query)) {
                row.show();
            } else {
                row.hide();
            }
        });
        
        // Mostrar mensagem se nenhum resultado
        const visibleRows = table.find('tbody tr:visible').length;
        if (visibleRows === 0) {
            if (!table.find('.no-results').length) {
                table.find('tbody').append(`
                    <tr class="no-results">
                        <td colspan="100%" class="text-center py-4">
                            <i class="fas fa-search fa-2x text-muted mb-2"></i>
                            <p class="text-muted">Nenhum resultado encontrado</p>
                        </td>
                    </tr>
                `);
            }
        } else {
            table.find('.no-results').remove();
        }
    });
}

// Inicializar componentes específicos baseado na página
function initializePageSpecific() {
    const page = $('body').data('page');
    
    switch(page) {
        case 'dashboard':
            initializeDashboard();
            break;
        case 'produtos':
            initializeProdutos();
            break;
        case 'vendas':
            initializeVendas();
            break;
        case 'qualidade':
            initializeQualidade();
            break;
        case 'reclamacoes':
            initializeReclamacoes();
            break;
    }
}

// Funções específicas por página
function initializeDashboard() {
    // Atualizar métricas periodicamente
    setInterval(function() {
        updateDashboardMetrics();
    }, 60000); // A cada minuto
}

function initializeProdutos() {
    // Busca em tempo real na tabela de produtos
    initializeRealTimeSearch('#search-produtos', '#produtos-table');
    
    // Autocomplete para categorias e fornecedores
    initializeAutocomplete('#categoria-search', '/ajax/buscar-categorias/');
    initializeAutocomplete('#fornecedor-search', '/ajax/buscar-fornecedores/');
}

function initializeVendas() {
    // Calculadora de totais em tempo real
    $('.item-quantidade, .item-preco').on('input', function() {
        calculateVendaTotal();
    });
}

function initializeQualidade() {
    // Validação de notas (1-5)
    $('.nota-qualidade').on('input', function() {
        const value = parseInt($(this).val());
        if (value < 1 || value > 5) {
            showFieldError($(this), 'Nota deve ser entre 1 e 5');
        }
    });
}

function initializeReclamacoes() {
    // Auto-gerar protocolo
    if ($('#numero_protocolo').val() === '') {
        $('#numero_protocolo').val(generateProtocol());
    }
}

// Utilitários específicos
function generateProtocol() {
    const timestamp = Date.now().toString().slice(-6);
    const random = Math.random().toString(36).substr(2, 3).toUpperCase();
    return `REC${timestamp}${random}`;
}

function calculateVendaTotal() {
    let total = 0;
    $('.item-row').each(function() {
        const quantidade = parseFloat($(this).find('.item-quantidade').val()) || 0;
        const preco = parseFloat($(this).find('.item-preco').val()) || 0;
        const subtotal = quantidade * preco;
        
        $(this).find('.item-subtotal').text(formatCurrency(subtotal));
        total += subtotal;
    });
    
    const desconto = parseFloat($('#desconto').val()) || 0;
    const valorFinal = total - desconto;
    
    $('#valor-total').text(formatCurrency(total));
    $('#valor-final').text(formatCurrency(valorFinal));
}

// Inicializar quando a página carregar
$(document).ready(function() {
    initializePageSpecific();
});
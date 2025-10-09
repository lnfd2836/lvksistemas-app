/**
 * JavaScript para configuração da Caixa Econômica Federal
 */

// Função para mostrar formulário
function mostrarFormulario() {
    var formContainer = document.getElementById('config-form-container');
    if (formContainer) {
        formContainer.style.display = 'block';
        formContainer.classList.remove('config-form-hidden');
        formContainer.classList.add('config-form-visible');
        formContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        var firstInput = document.getElementById('agencia');
        if (firstInput) {
            setTimeout(function() { firstInput.focus(); }, 300);
        }
    }
}

// Função para editar configuração
function editarConfiguracao() {
    mostrarFormulario();
}

// Função para cancelar edição
function cancelarEdicao() {
    var formContainer = document.getElementById('config-form-container');
    if (formContainer) {
        formContainer.classList.remove('config-form-visible');
        formContainer.classList.add('config-form-hidden');
        setTimeout(function() {
            formContainer.style.display = 'none';
        }, 300);
    }
}

// Validações específicas da Caixa
document.addEventListener('DOMContentLoaded', function() {
    // Formatação de CNPJ
    var cnpjInput = document.getElementById('cnpj_beneficiario');
    if (cnpjInput) {
        cnpjInput.addEventListener('input', function(e) {
            var value = e.target.value.replace(/\D/g, '');
            if (value.length <= 14) {
                value = value.replace(/^(\d{2})(\d)/, '$1.$2');
                value = value.replace(/^(\d{2})\.(\d{3})(\d)/, '$1.$2.$3');
                value = value.replace(/\.(\d{3})(\d)/, '.$1/$2');
                value = value.replace(/(\d{4})(\d)/, '$1-$2');
                e.target.value = value;
            }
        });
    }

    // Validação de agência (4 dígitos)
    var agenciaInput = document.getElementById('agencia');
    if (agenciaInput) {
        agenciaInput.addEventListener('input', function(e) {
            var value = e.target.value.replace(/\D/g, '');
            if (value.length > 4) {
                value = value.substring(0, 4);
            }
            e.target.value = value;
        });
    }

    // Validação do formulário
    var form = document.getElementById('boleto-config-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            var agencia = document.getElementById('agencia').value;
            var conta = document.getElementById('conta').value;
            var cedente = document.getElementById('codigo_cedente').value;
            var convenio = document.getElementById('convenio').value;
            
            if (!agencia || !conta || !cedente || !convenio) {
                alert('Por favor, preencha todos os campos obrigatórios da Caixa!');
                e.preventDefault();
                return;
            }
            
            if (agencia.length !== 4) {
                alert('A agência deve ter exatamente 4 dígitos!');
                e.preventDefault();
                return;
            }
            
            var mensagem = 'ATENÇÃO!\n\n' +
                'Você está configurando boletos REAIS da Caixa Econômica Federal.\n' +
                'Os pagamentos irão para sua conta real.\n\n' +
                'Dados informados:\n' +
                'Agência: ' + agencia + '\n' +
                'Conta: ' + conta + '\n' +
                'Cedente: ' + cedente + '\n' +
                'Convênio: ' + convenio + '\n\n' +
                'Confirma que todos os dados estão corretos?';
            
            if (!confirm(mensagem)) {
                e.preventDefault();
            }
        });
    }
});
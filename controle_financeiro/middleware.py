from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from controle_financeiro.models import ControleFinanceiro
from django.utils import timezone


class ControleFinanceiroMiddleware:
    """Middleware para verificar o status financeiro das lojas"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verifica se o usuário está logado e não é super admin
        if (request.user.is_authenticated and 
            not request.user.is_superuser and 
            hasattr(request, 'loja_atual') and 
            request.loja_atual):
            
            try:
                # Busca o controle financeiro da loja
                controle = ControleFinanceiro.objects.get(loja=request.loja_atual)
                
                # Verifica o status financeiro
                controle.verificar_status()
                
                # Se a loja está bloqueada, redireciona para página de pagamento
                if controle.bloqueada:
                    # URLs que o usuário pode acessar mesmo bloqueado
                    urls_permitidas = [
                        '/financeiro/pagamento/',
                        '/financeiro/boletos-cliente/',
                        '/financeiro/asaas/webhook/',  # Webhook do Asaas não precisa de verificação
                        '/logout/',
                        '/loja/login/',
                    ]
                    
                    # Se não está em uma URL permitida, redireciona
                    if not any(request.path.startswith(url) for url in urls_permitidas):
                        messages.error(
                            request, 
                            f'Sua conta está bloqueada. Motivo: {controle.motivo_bloqueio}'
                        )
                        return redirect('controle_financeiro:pagamento_cliente')
                
                # Se está próxima do vencimento (5 dias), mostra aviso
                elif controle.dias_para_vencimento <= 5 and controle.dias_para_vencimento > 0:
                    if not request.path.startswith('/financeiro/pagamento/'):
                        messages.warning(
                            request, 
                            f'Sua conta vence em {controle.dias_para_vencimento} dias. '
                            f'Renove agora para evitar bloqueio.'
                        )
                
            except ControleFinanceiro.DoesNotExist:
                # Se não tem controle financeiro, permite acesso normal
                pass

        response = self.get_response(request)
        return response

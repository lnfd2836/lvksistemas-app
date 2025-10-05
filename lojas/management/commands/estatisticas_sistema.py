"""
Comando para gerar estatísticas do sistema
"""
from django.core.management.base import BaseCommand
from django.db.models import Count, Sum
from django.utils import timezone
from lojas.models import Loja, Cliente, Produto, Venda
from usuarios.models import LogAcesso
from dashboard.models import Notificacao


class Command(BaseCommand):
    help = 'Gera estatísticas do sistema'

    def handle(self, *args, **options):
        try:
            # Estatísticas gerais
            total_lojas = Loja.objects.count()
            lojas_ativas = Loja.objects.filter(status='ativa').count()
            total_clientes = Cliente.objects.count()
            total_produtos = Produto.objects.count()
            total_vendas = Venda.objects.count()
            
            # Receita total
            receita_total = Venda.objects.filter(status='concluida').aggregate(
                total=Sum('valor_final')
            )['total'] or 0
            
            # Logs de acesso
            total_logs = LogAcesso.objects.count()
            logs_hoje = LogAcesso.objects.filter(
                data_acesso__date=timezone.now().date()
            ).count()
            
            # Notificações
            total_notificacoes = Notificacao.objects.count()
            notificacoes_nao_lidas = Notificacao.objects.filter(lida=False).count()
            
            # Exibe as estatísticas
            self.stdout.write(self.style.SUCCESS('=== ESTATÍSTICAS DO SISTEMA ==='))
            self.stdout.write(f'Total de Lojas: {total_lojas}')
            self.stdout.write(f'Lojas Ativas: {lojas_ativas}')
            self.stdout.write(f'Total de Clientes: {total_clientes}')
            self.stdout.write(f'Total de Produtos: {total_produtos}')
            self.stdout.write(f'Total de Vendas: {total_vendas}')
            self.stdout.write(f'Receita Total: R$ {receita_total:.2f}')
            self.stdout.write(f'Total de Logs: {total_logs}')
            self.stdout.write(f'Logs Hoje: {logs_hoje}')
            self.stdout.write(f'Total de Notificações: {total_notificacoes}')
            self.stdout.write(f'Notificações Não Lidas: {notificacoes_nao_lidas}')
            
            # Estatísticas por loja
            self.stdout.write(self.style.SUCCESS('\n=== ESTATÍSTICAS POR LOJA ==='))
            for loja in Loja.objects.all():
                clientes_loja = Cliente.objects.filter(loja=loja).count()
                produtos_loja = Produto.objects.filter(loja=loja).count()
                vendas_loja = Venda.objects.filter(loja=loja).count()
                receita_loja = Venda.objects.filter(
                    loja=loja, status='concluida'
                ).aggregate(total=Sum('valor_final'))['total'] or 0
                
                self.stdout.write(f'\n{loja.nome}:')
                self.stdout.write(f'  Clientes: {clientes_loja}')
                self.stdout.write(f'  Produtos: {produtos_loja}')
                self.stdout.write(f'  Vendas: {vendas_loja}')
                self.stdout.write(f'  Receita: R$ {receita_loja:.2f}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao gerar estatísticas: {e}')
            )

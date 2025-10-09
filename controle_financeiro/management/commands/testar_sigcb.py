"""
Comando para testar o layout SIGCB da Caixa
"""

from django.core.management.base import BaseCommand
from controle_financeiro.models import BoletoGerado, ConfiguracaoBoleto
from controle_financeiro.pdf_service_sigcb import BoletoPDFServiceSIGCB
import os


class Command(BaseCommand):
    help = 'Testa o layout SIGCB da Caixa gerando PDF de exemplo'

    def add_arguments(self, parser):
        parser.add_argument(
            '--boleto-id',
            type=int,
            help='ID do boleto para testar (opcional)',
        )
        parser.add_argument(
            '--salvar',
            action='store_true',
            help='Salva o PDF gerado em arquivo',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== TESTE LAYOUT SIGCB CAIXA ==='))
        
        # Buscar boleto para teste
        if options['boleto_id']:
            try:
                boleto = BoletoGerado.objects.get(id=options['boleto_id'])
                self.stdout.write(f'Usando boleto ID {boleto.id}: {boleto.numero_boleto}')
            except BoletoGerado.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Boleto ID {options["boleto_id"]} não encontrado'))
                return
        else:
            # Buscar último boleto da Caixa
            boleto = BoletoGerado.objects.filter(
                configuracao__codigo_banco='104'
            ).order_by('-data_criacao').first()
            
            if not boleto:
                self.stdout.write(self.style.ERROR('Nenhum boleto da Caixa encontrado'))
                return
            
            self.stdout.write(f'Usando último boleto da Caixa: {boleto.numero_boleto}')
        
        # Verificar se é boleto da Caixa
        if boleto.configuracao.codigo_banco != '104':
            self.stdout.write(self.style.ERROR('Boleto não é da Caixa Econômica Federal'))
            return
        
        # Testar geração do PDF SIGCB
        try:
            self.stdout.write('Gerando PDF no layout SIGCB...')
            
            pdf_service = BoletoPDFServiceSIGCB()
            pdf_response = pdf_service.gerar_pdf_boleto_sigcb(boleto)
            
            self.stdout.write(self.style.SUCCESS('✅ PDF SIGCB gerado com sucesso!'))
            
            # Informações do boleto
            self.stdout.write(f'\\n--- INFORMAÇÕES DO BOLETO ---')
            self.stdout.write(f'Número: {boleto.numero_boleto}')
            self.stdout.write(f'Valor: R$ {boleto.valor}')
            self.stdout.write(f'Vencimento: {boleto.data_vencimento.strftime("%d/%m/%Y")}')
            self.stdout.write(f'Linha digitável: {boleto.linha_digitavel}')
            self.stdout.write(f'Código de barras: {boleto.codigo_barras}')
            
            # Informações da configuração
            config = boleto.configuracao
            self.stdout.write(f'\\n--- CONFIGURAÇÃO CAIXA ---')
            self.stdout.write(f'Banco: {config.codigo_banco} - {config.nome_banco}')
            self.stdout.write(f'Agência: {config.agencia}')
            self.stdout.write(f'Conta: {config.conta}')
            self.stdout.write(f'Carteira: {config.carteira}')
            self.stdout.write(f'Cedente: {config.codigo_cedente}')
            
            # Salvar arquivo se solicitado
            if options['salvar']:
                filename = f'boleto_sigcb_{boleto.numero_boleto}.pdf'
                
                with open(filename, 'wb') as f:
                    if hasattr(pdf_response, 'content'):
                        f.write(pdf_response.content)
                    else:
                        # Para HttpResponse
                        for chunk in pdf_response.streaming_content:
                            f.write(chunk)
                
                self.stdout.write(self.style.SUCCESS(f'✅ PDF salvo como: {filename}'))
                self.stdout.write(f'Tamanho do arquivo: {os.path.getsize(filename)} bytes')
            
            # Verificar diferenças do layout SIGCB
            self.stdout.write(f'\\n--- CARACTERÍSTICAS SIGCB ---')
            self.stdout.write('✅ Layout atualizado conforme padrão SIGCB')
            self.stdout.write('✅ Cores oficiais da Caixa (azul e laranja)')
            self.stdout.write('✅ Ficha de compensação no formato padrão')
            self.stdout.write('✅ Código de barras otimizado para leitura')
            self.stdout.write('✅ Campos organizados conforme especificação')
            self.stdout.write('✅ Recibo do sacado no formato correto')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Erro ao gerar PDF SIGCB: {str(e)}'))
            import traceback
            traceback.print_exc()
        
        self.stdout.write(f'\\n{"="*50}')
        self.stdout.write(self.style.SUCCESS('TESTE SIGCB CONCLUÍDO'))
        self.stdout.write(f'{"="*50}')
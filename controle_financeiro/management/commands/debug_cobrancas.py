from django.core.management.base import BaseCommand
from controle_financeiro.models import CobrancaAsaas

class Command(BaseCommand):
    help = 'Debug das cobranças Asaas no banco de dados'

    def handle(self, *args, **options):
        self.stdout.write("=== DEBUG COBRANÇAS ASAAS ===")
        
        # Contar total de cobranças
        total = CobrancaAsaas.objects.count()
        self.stdout.write(f"Total de cobranças no banco: {total}")
        
        if total > 0:
            # Listar todas as cobranças
            self.stdout.write("\n=== LISTA DE COBRANÇAS ===")
            for cobranca in CobrancaAsaas.objects.all():
                self.stdout.write(f"ID: {cobranca.id}")
                self.stdout.write(f"Asaas ID: {cobranca.asaas_id}")
                self.stdout.write(f"Valor: R$ {cobranca.valor}")
                self.stdout.write(f"Status: {cobranca.status}")
                self.stdout.write(f"Data Criação: {cobranca.data_criacao}")
                self.stdout.write(f"Data Vencimento: {cobranca.data_vencimento}")
                
                if cobranca.controle_financeiro:
                    self.stdout.write(f"Loja: {cobranca.controle_financeiro.loja.nome}")
                else:
                    self.stdout.write("Loja: ERRO - Controle financeiro não encontrado")
                
                self.stdout.write(f"Bank Slip URL: {cobranca.bank_slip_url}")
                self.stdout.write(f"PIX QR Code: {'Sim' if cobranca.pix_qr_code else 'Não'}")
                if cobranca.pix_copy_paste:
                    self.stdout.write(f"PIX Copia e Cola: {cobranca.pix_copy_paste[:50]}...")
                if cobranca.pix_expires_date:
                    self.stdout.write(f"PIX Expira em: {cobranca.pix_expires_date}")
                self.stdout.write("-" * 50)
        else:
            self.stdout.write("Nenhuma cobrança encontrada no banco de dados")
        
        self.stdout.write("\n=== FIM DEBUG ===")
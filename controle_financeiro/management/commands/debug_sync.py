"""
Management command para debugar a sincronização
"""
from django.core.management.base import BaseCommand
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from controle_financeiro.asaas_service import AsaasService
from controle_financeiro.models import CobrancaAsaas, ControleFinanceiro

class Command(BaseCommand):
    help = 'Debug da sincronização com Asaas'
    
    def handle(self, *args, **options):
        self.stdout.write("🔍 INICIANDO DEBUG DA SINCRONIZAÇÃO ASAAS")
        self.stdout.write("=" * 50)
        
        try:
            # 1. Testar configuração
            asaas_service = AsaasService()
            self.stdout.write(f"🔧 Base URL: {asaas_service.base_url}")
            self.stdout.write(f"🔧 Environment: {asaas_service.environment}")
            
            # 2. Validar configuração
            self.stdout.write("\n📡 Testando conectividade...")
            if asaas_service.validar_configuracao():
                self.stdout.write(self.style.SUCCESS("✅ Configuração válida!"))
            else:
                self.stdout.write(self.style.ERROR("❌ Configuração inválida!"))
                return
            
            # 3. Buscar cobranças no Asaas (últimos 30 dias)
            self.stdout.write("\n🔍 Buscando cobranças no Asaas...")
            data_inicio = (timezone.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            response = requests.get(
                f"{asaas_service.base_url}/payments",
                headers=asaas_service.headers,
                params={
                    'dateCreated[ge]': data_inicio,
                    'limit': 100
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                payments = data.get('data', [])
                
                self.stdout.write(f"📊 Encontradas {len(payments)} cobranças no Asaas")
                
                if payments:
                    self.stdout.write("\n📋 COBRANÇAS ENCONTRADAS NO ASAAS:")
                    self.stdout.write("-" * 80)
                    for i, payment in enumerate(payments[:10]):  # Mostrar apenas as 10 primeiras
                        self.stdout.write(f"{i+1:2d}. ID: {payment['id']}")
                        self.stdout.write(f"    Status: {payment['status']}")
                        self.stdout.write(f"    Valor: R$ {payment['value']}")
                        self.stdout.write(f"    Vencimento: {payment['dueDate']}")
                        self.stdout.write(f"    Customer: {payment['customer']}")
                        self.stdout.write(f"    External Ref: {payment.get('externalReference', 'N/A')}")
                        self.stdout.write(f"    Descrição: {payment.get('description', 'N/A')}")
                        self.stdout.write("")
                else:
                    self.stdout.write(self.style.WARNING("❌ Nenhuma cobrança encontrada no Asaas!"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Erro ao buscar cobranças: {response.status_code}"))
                self.stdout.write(f"Response: {response.text}")
            
            # 4. Verificar cobranças no sistema local
            self.stdout.write("\n🗄️ Verificando cobranças no sistema local...")
            cobrancas_locais = CobrancaAsaas.objects.all().count()
            self.stdout.write(f"📊 Total de cobranças no sistema: {cobrancas_locais}")
            
            if cobrancas_locais > 0:
                self.stdout.write("\n📋 COBRANÇAS NO SISTEMA LOCAL:")
                self.stdout.write("-" * 80)
                for cobranca in CobrancaAsaas.objects.all()[:10]:
                    self.stdout.write(f"ID Asaas: {cobranca.asaas_id}")
                    self.stdout.write(f"Status: {cobranca.status}")
                    self.stdout.write(f"Valor: R$ {cobranca.valor}")
                    self.stdout.write(f"Loja: {cobranca.controle_financeiro.loja.nome}")
                    self.stdout.write(f"Criado em: {cobranca.data_criacao}")
                    self.stdout.write("")
            
            # 5. Verificar controles financeiros
            self.stdout.write("\n🏪 Verificando controles financeiros...")
            controles = ControleFinanceiro.objects.all().count()
            self.stdout.write(f"📊 Total de controles financeiros: {controles}")
            
            if controles > 0:
                self.stdout.write("\n📋 CONTROLES FINANCEIROS:")
                self.stdout.write("-" * 80)
                for controle in ControleFinanceiro.objects.all()[:5]:
                    self.stdout.write(f"ID: {controle.id}")
                    self.stdout.write(f"Loja: {controle.loja.nome}")
                    self.stdout.write(f"Email: {controle.loja.email}")
                    self.stdout.write(f"Status: {controle.status}")
                    self.stdout.write("")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro no debug: {str(e)}"))
            import traceback
            traceback.print_exc()
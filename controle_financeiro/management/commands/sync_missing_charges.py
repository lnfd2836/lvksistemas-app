"""
Management command para sincronizar cobranças que estão faltando
"""
from django.core.management.base import BaseCommand
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal
from controle_financeiro.asaas_service import AsaasService
from controle_financeiro.models import CobrancaAsaas, ControleFinanceiro, PlanoFinanceiro
from lojas.models import Loja

class Command(BaseCommand):
    help = 'Sincroniza cobranças que estão faltando do Asaas'
    
    def handle(self, *args, **options):
        self.stdout.write("🔄 SINCRONIZANDO COBRANÇAS FALTANTES")
        self.stdout.write("=" * 50)
        
        try:
            asaas_service = AsaasService()
            
            # Validar configuração
            if not asaas_service.validar_configuracao():
                self.stdout.write(self.style.ERROR("❌ Configuração da API Asaas inválida"))
                return
            
            # Buscar cobranças do Asaas
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
            
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f"❌ Erro ao buscar cobranças: {response.status_code}"))
                return
            
            data = response.json()
            payments = data.get('data', [])
            
            self.stdout.write(f"📊 Encontradas {len(payments)} cobranças no Asaas")
            
            total_criadas = 0
            total_erros = 0
            
            for payment in payments:
                try:
                    # Verificar se já existe
                    if CobrancaAsaas.objects.filter(asaas_id=payment['id']).exists():
                        continue
                    
                    self.stdout.write(f"🆕 Criando cobrança: {payment['id']}")
                    
                    # Tentar identificar controle financeiro
                    controle = self._identificar_controle_financeiro(payment, asaas_service)
                    
                    if not controle:
                        self.stdout.write(self.style.WARNING(f"⚠️ Não foi possível identificar controle para {payment['id']}"))
                        total_erros += 1
                        continue
                    
                    # Criar cobrança
                    from datetime import timezone as dt_timezone
                    cobranca = CobrancaAsaas.objects.create(
                        asaas_id=payment['id'],
                        controle_financeiro=controle,
                        customer_id=payment['customer'],
                        valor=Decimal(str(payment['value'])),
                        data_vencimento=datetime.fromisoformat(payment['dueDate']).replace(tzinfo=dt_timezone.utc),
                        descricao=payment.get('description', ''),
                        status=payment['status'],
                        external_reference=payment.get('externalReference', ''),
                        api_response=payment
                    )
                    
                    # Atualizar dados adicionais
                    cobranca.atualizar_dados_asaas(payment)
                    
                    total_criadas += 1
                    self.stdout.write(self.style.SUCCESS(f"✅ Cobrança {payment['id']} criada com sucesso"))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Erro ao criar cobrança {payment.get('id', 'N/A')}: {str(e)}"))
                    total_erros += 1
            
            self.stdout.write("\n" + "=" * 50)
            self.stdout.write(self.style.SUCCESS(f"✅ Sincronização concluída!"))
            self.stdout.write(f"📊 Cobranças criadas: {total_criadas}")
            self.stdout.write(f"❌ Erros: {total_erros}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro geral: {str(e)}"))
            import traceback
            traceback.print_exc()
    
    def _identificar_controle_financeiro(self, payment_data, asaas_service):
        """Identifica o controle financeiro para uma cobrança"""
        
        # 1. Por externalReference
        external_ref = payment_data.get('externalReference', '')
        if external_ref and external_ref.startswith('CF_'):
            cf_id = external_ref.split('_')[1]
            try:
                controle = ControleFinanceiro.objects.get(id=cf_id)
                self.stdout.write(f"   📋 Controle encontrado por externalReference: {controle.loja.nome}")
                return controle
            except ControleFinanceiro.DoesNotExist:
                self.stdout.write(f"   ⚠️ Controle {cf_id} não encontrado")
        
        # 2. Por dados do customer
        customer_id = payment_data.get('customer')
        if customer_id:
            try:
                # Buscar dados do customer
                customer_response = requests.get(
                    f"{asaas_service.base_url}/customers/{customer_id}",
                    headers=asaas_service.headers,
                    timeout=10
                )
                
                if customer_response.status_code == 200:
                    customer_data = customer_response.json()
                    customer_email = customer_data.get('email', '')
                    customer_cnpj = customer_data.get('cpfCnpj', '')
                    
                    # Buscar por email
                    if customer_email:
                        controle = ControleFinanceiro.objects.filter(
                            loja__email=customer_email
                        ).first()
                        if controle:
                            self.stdout.write(f"   📧 Controle encontrado por email: {controle.loja.nome}")
                            return controle
                    
                    # Buscar por CNPJ
                    if customer_cnpj:
                        controle = ControleFinanceiro.objects.filter(
                            loja__cnpj=customer_cnpj
                        ).first()
                        if controle:
                            self.stdout.write(f"   🏢 Controle encontrado por CNPJ: {controle.loja.nome}")
                            return controle
                    
                    # Criar automaticamente se não encontrou
                    self.stdout.write(f"   🆕 Criando loja e controle automaticamente para customer {customer_id}")
                    return self._criar_loja_e_controle_automatico(customer_data, payment_data)
                    
            except Exception as e:
                self.stdout.write(f"   ❌ Erro ao buscar customer {customer_id}: {str(e)}")
        
        return None
    
    def _criar_loja_e_controle_automatico(self, customer_data, payment_data):
        """Cria automaticamente loja e controle financeiro"""
        try:
            # Dados do customer
            customer_name = customer_data.get('name', 'Loja Importada do Asaas')
            customer_email = customer_data.get('email', '')
            customer_cnpj = customer_data.get('cpfCnpj', '')
            customer_phone = customer_data.get('phone', '')
            
            # Criar loja
            loja = Loja.objects.create(
                nome=customer_name,
                email=customer_email,
                cnpj=customer_cnpj,
                telefone=customer_phone,
                endereco=customer_data.get('address', 'Endereço não informado'),
                cidade=customer_data.get('city', 'Cidade não informada'),
                estado=customer_data.get('state', 'Estado não informado'),
                cep='00000000',
                status='ativa'
            )
            
            # Buscar plano padrão
            plano_padrao = PlanoFinanceiro.objects.filter(nome='Básico').first()
            if not plano_padrao:
                plano_padrao = PlanoFinanceiro.objects.create(
                    nome='Básico',
                    descricao='Plano básico para lojas importadas',
                    valor_mensal=29.90,
                    ativo=True
                )
            
            # Criar controle financeiro
            controle = ControleFinanceiro.objects.create(
                loja=loja,
                plano=plano_padrao,
                status='ativa',
                valor_mensal=plano_padrao.valor_mensal,
                data_inicio=timezone.now(),
                data_vencimento=timezone.now() + timedelta(days=30)
            )
            
            self.stdout.write(f"   ✅ Loja e controle criados: {loja.nome} (ID: {controle.id})")
            return controle
            
        except Exception as e:
            self.stdout.write(f"   ❌ Erro ao criar loja e controle: {str(e)}")
            return None
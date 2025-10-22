"""
Comando para testar geração completa de cobrança com PIX
"""

from django.core.management.base import BaseCommand
from controle_financeiro.models import ControleFinanceiro
from controle_financeiro.asaas_service import AsaasService
import json

class Command(BaseCommand):
    help = 'Testa geração completa de cobrança com PIX no Asaas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--controle-id',
            type=int,
            help='ID do controle financeiro para testar',
        )

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("🧪 TESTE COMPLETO DE COBRANÇA COM PIX")
        self.stdout.write("=" * 60)
        
        # Buscar controle financeiro
        if options['controle_id']:
            try:
                controle = ControleFinanceiro.objects.get(id=options['controle_id'])
            except ControleFinanceiro.DoesNotExist:
                self.stdout.write(f"❌ Controle financeiro {options['controle_id']} não encontrado")
                return
        else:
            controle = ControleFinanceiro.objects.first()
            if not controle:
                self.stdout.write("❌ Nenhum controle financeiro encontrado")
                return
        
        self.stdout.write(f"📋 Testando com:")
        self.stdout.write(f"   ID: {controle.id}")
        self.stdout.write(f"   Loja: {controle.loja.nome}")
        self.stdout.write(f"   Plano: {controle.plano.nome}")
        self.stdout.write(f"   Valor: R$ {controle.valor_mensal}")
        self.stdout.write("")
        
        # Criar serviço Asaas
        try:
            asaas_service = AsaasService()
            self.stdout.write("✅ AsaasService criado")
        except Exception as e:
            self.stdout.write(f"❌ Erro ao criar AsaasService: {str(e)}")
            return
        
        # Testar validação
        self.stdout.write("🔍 Validando configuração...")
        if not asaas_service.validar_configuracao():
            self.stdout.write("❌ Configuração inválida")
            return
        
        self.stdout.write("✅ Configuração válida")
        
        # Gerar cobrança
        self.stdout.write("\n💰 Gerando cobrança com PIX...")
        
        try:
            resultado = asaas_service.gerar_cobranca_com_pix(
                controle, 
                dias_vencimento=30,
                descricao=f"Teste - Mensalidade {controle.plano.nome} - {controle.loja.nome}"
            )
            
            if resultado.get('success'):
                self.stdout.write(self.style.SUCCESS("🎉 COBRANÇA CRIADA COM SUCESSO!"))
                
                cobranca = resultado['cobranca']
                self.stdout.write(f"\n📄 DADOS DA COBRANÇA:")
                self.stdout.write(f"   ID: {cobranca['id']}")
                self.stdout.write(f"   Valor: R$ {cobranca['value']}")
                self.stdout.write(f"   Vencimento: {cobranca['dueDate']}")
                self.stdout.write(f"   Status: {cobranca['status']}")
                self.stdout.write(f"   Link do Boleto: {cobranca.get('bankSlipUrl', 'N/A')}")
                
                # Dados do PIX
                if resultado.get('pix'):
                    pix = resultado['pix']
                    self.stdout.write(f"\n💳 DADOS DO PIX:")
                    self.stdout.write(f"   Payload: {pix.get('payload', 'N/A')[:50]}...")
                    self.stdout.write(f"   QR Code: {pix.get('encodedImage', 'Disponível' if pix.get('encodedImage') else 'N/A')}")
                    self.stdout.write(f"   Expira em: {pix.get('expirationDate', 'N/A')}")
                else:
                    self.stdout.write(f"\n⚠️ PIX não foi gerado")
                
                # Cliente
                if resultado.get('cliente'):
                    cliente = resultado['cliente']
                    self.stdout.write(f"\n👤 CLIENTE:")
                    self.stdout.write(f"   ID: {cliente['id']}")
                    self.stdout.write(f"   Nome: {cliente['name']}")
                    self.stdout.write(f"   Email: {cliente['email']}")
                
                # URLs importantes
                self.stdout.write(f"\n🔗 LINKS IMPORTANTES:")
                self.stdout.write(f"   Sistema: https://lvksistemas-app-4f6fa281e217.herokuapp.com")
                self.stdout.write(f"   Admin: https://lvksistemas-app-4f6fa281e217.herokuapp.com/admin/")
                self.stdout.write(f"   Cobranças: https://lvksistemas-app-4f6fa281e217.herokuapp.com/financeiro/asaas/cobrancas/")
                
            else:
                self.stdout.write(self.style.ERROR("❌ ERRO AO CRIAR COBRANÇA"))
                self.stdout.write(f"Erro: {resultado.get('error', 'Desconhecido')}")
                
                if 'details' in resultado:
                    try:
                        details = json.loads(resultado['details'])
                        if 'errors' in details:
                            for error in details['errors']:
                                self.stdout.write(f"   - {error.get('description', error)}")
                    except:
                        self.stdout.write(f"Detalhes: {resultado['details']}")
                
                # Sugestões de solução
                error_msg = str(resultado.get('error', '')) + str(resultado.get('details', ''))
                
                if 'domínio' in error_msg.lower():
                    self.stdout.write(f"\n💡 SOLUÇÃO:")
                    self.stdout.write(f"1. Acesse: https://www.asaas.com")
                    self.stdout.write(f"2. Vá em: Minha Conta → Informações")
                    self.stdout.write(f"3. Adicione o domínio: lvksistemas-app-4f6fa281e217.herokuapp.com")
                    self.stdout.write(f"4. Salve as alterações")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ EXCEÇÃO: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("🏁 TESTE FINALIZADO")
        self.stdout.write("=" * 60)
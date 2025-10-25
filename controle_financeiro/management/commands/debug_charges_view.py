"""
Management command para debugar a view de cobranças
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from controle_financeiro.models import CobrancaAsaas

class Command(BaseCommand):
    help = 'Debug da view de cobranças'
    
    def handle(self, *args, **options):
        self.stdout.write("🔍 DEBUGANDO VIEW DE COBRANÇAS")
        self.stdout.write("=" * 50)
        
        try:
            # 1. Verificar usuários
            self.stdout.write("\n👥 USUÁRIOS NO SISTEMA:")
            users = User.objects.all()
            for user in users:
                self.stdout.write(f"- {user.username} (superuser: {user.is_superuser})")
            
            # 2. Verificar cobranças totais
            total_cobrancas = CobrancaAsaas.objects.count()
            self.stdout.write(f"\n📊 TOTAL DE COBRANÇAS: {total_cobrancas}")
            
            if total_cobrancas > 0:
                # 3. Verificar cobranças por usuário
                self.stdout.write("\n📋 COBRANÇAS POR USUÁRIO:")
                
                for user in users:
                    if user.is_superuser:
                        # Super admin vê todas
                        cobrancas_user = CobrancaAsaas.objects.all()
                        self.stdout.write(f"- {user.username} (superuser): {cobrancas_user.count()} cobranças")
                    else:
                        # Admin de loja vê apenas suas
                        try:
                            cobrancas_user = CobrancaAsaas.objects.filter(
                                controle_financeiro__loja__admin_user=user
                            )
                            self.stdout.write(f"- {user.username} (loja admin): {cobrancas_user.count()} cobranças")
                        except Exception as e:
                            self.stdout.write(f"- {user.username} (loja admin): ERRO - {str(e)}")
                
                # 4. Listar algumas cobranças
                self.stdout.write("\n📋 PRIMEIRAS 10 COBRANÇAS:")
                self.stdout.write("-" * 80)
                for cobranca in CobrancaAsaas.objects.all()[:10]:
                    loja_nome = cobranca.controle_financeiro.loja.nome if cobranca.controle_financeiro and cobranca.controle_financeiro.loja else "N/A"
                    loja_admin = cobranca.controle_financeiro.loja.admin_user.username if cobranca.controle_financeiro and cobranca.controle_financeiro.loja and cobranca.controle_financeiro.loja.admin_user else "N/A"
                    
                    self.stdout.write(f"ID: {cobranca.asaas_id}")
                    self.stdout.write(f"  Loja: {loja_nome}")
                    self.stdout.write(f"  Admin da Loja: {loja_admin}")
                    self.stdout.write(f"  Valor: R$ {cobranca.valor}")
                    self.stdout.write(f"  Status: {cobranca.status}")
                    self.stdout.write(f"  Criado: {cobranca.data_criacao}")
                    self.stdout.write("")
                
                # 5. Verificar lojas sem admin
                self.stdout.write("\n🏪 VERIFICANDO LOJAS SEM ADMIN:")
                cobrancas_sem_admin = CobrancaAsaas.objects.filter(
                    controle_financeiro__loja__admin_user__isnull=True
                )
                self.stdout.write(f"Cobranças de lojas sem admin: {cobrancas_sem_admin.count()}")
                
                if cobrancas_sem_admin.count() > 0:
                    for cobranca in cobrancas_sem_admin[:5]:
                        loja_nome = cobranca.controle_financeiro.loja.nome if cobranca.controle_financeiro and cobranca.controle_financeiro.loja else "N/A"
                        self.stdout.write(f"  - {cobranca.asaas_id} (Loja: {loja_nome})")
            
            else:
                self.stdout.write("❌ Nenhuma cobrança encontrada no sistema!")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Erro no debug: {str(e)}"))
            import traceback
            traceback.print_exc()
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from lojas.models import Loja
from controle_financeiro.models import PlanoFinanceiro, ControleFinanceiro, ConfiguracaoBoleto, BoletoGerado


class Command(BaseCommand):
    help = 'Testa a criação de uma loja com geração automática de boleto'

    def handle(self, *args, **options):
        try:
            # Cria usuário administrador
            admin_user = User.objects.create_user(
                username='teste@loja.com',
                email='teste@loja.com',
                first_name='Loja',
                last_name='Teste',
                is_staff=True,
            )
            admin_user.set_password('123456')
            admin_user.save()
            
            # Cria a loja
            loja = Loja.objects.create(
                nome='Loja Teste Automática',
                cnpj='12.345.678/0001-90',
                email='teste@loja.com',
                telefone='(11) 99999-9999',
                endereco='Rua Teste, 123',
                cidade='São Paulo',
                estado='SP',
                cep='01234-567',
                status='ativa',
                admin_user=admin_user,
                senha_provisoria='123456'
            )
            
            # Busca o plano básico
            plano_basico = PlanoFinanceiro.objects.filter(ativo=True).first()
            if not plano_basico:
                plano_basico = PlanoFinanceiro.objects.create(
                    nome="Básico",
                    descricao="Plano básico para novas lojas",
                    valor_mensal=29.90,
                    dias_trial=30,
                    ativo=True
                )
            
            # Cria o controle financeiro
            controle_financeiro = ControleFinanceiro.objects.create(
                loja=loja,
                plano=plano_basico,
                status='ativa',
                valor_mensal=plano_basico.valor_mensal,
                data_inicio=timezone.now(),
                data_vencimento=timezone.now() + timedelta(days=plano_basico.dias_trial)
            )
            
            # Gera boleto automaticamente
            configuracao_boleto = ConfiguracaoBoleto.objects.filter(ativo=True).first()
            if configuracao_boleto:
                numero_boleto = f"BOL{timezone.now().strftime('%Y%m%d%H%M%S')}"
                linha_digitavel = f"23791{configuracao_boleto.agencia.zfill(4)}{configuracao_boleto.conta.zfill(8)}{numero_boleto.zfill(10)}"
                codigo_barras = linha_digitavel.replace(' ', '')
                
                boleto = BoletoGerado.objects.create(
                    controle_financeiro=controle_financeiro,
                    configuracao=configuracao_boleto,
                    numero_boleto=numero_boleto,
                    linha_digitavel=linha_digitavel,
                    codigo_barras=codigo_barras,
                    valor=plano_basico.valor_mensal,
                    data_vencimento=timezone.now() + timedelta(days=7),
                    status='pendente'
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Loja "{loja.nome}" criada com sucesso!')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Controle financeiro criado: R$ {controle_financeiro.valor_mensal}')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Boleto gerado: {boleto.numero_boleto} - R$ {boleto.valor}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Nenhuma configuração de boleto ativa encontrada')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao criar loja: {str(e)}')
            )

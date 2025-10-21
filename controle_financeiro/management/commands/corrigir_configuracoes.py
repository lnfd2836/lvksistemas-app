from django.core.management.base import BaseCommand
from controle_financeiro.models import ConfiguracaoBoleto, BoletoGerado, CobrancaAsaas

class Command(BaseCommand):
    help = 'Corrige configurações de boleto para usar apenas Asaas'

    def handle(self, *args, **options):
        self.stdout.write('🔍 DIAGNÓSTICO DAS CONFIGURAÇÕES DE BOLETO')
        self.stdout.write('=' * 50)

        # 1. Verificar configurações existentes
        self.stdout.write('\n1️⃣ CONFIGURAÇÕES EXISTENTES:')
        configs = ConfiguracaoBoleto.objects.all()
        for config in configs:
            self.stdout.write(f'   ID: {config.id}, Banco: {config.codigo_banco} ({config.nome_banco}), Ativo: {config.ativo}')

        # 2. Verificar se existe configuração do Asaas
        self.stdout.write('\n2️⃣ CONFIGURAÇÃO DO ASAAS:')
        config_asaas = ConfiguracaoBoleto.objects.filter(codigo_banco="461").first()
        if config_asaas:
            self.stdout.write(f'   ✅ Configuração Asaas encontrada: ID {config_asaas.id}')
            self.stdout.write(f'   Ativo: {config_asaas.ativo}')
            self.stdout.write(f'   Nome: {config_asaas.nome_banco}')
        else:
            self.stdout.write('   ❌ Configuração Asaas NÃO encontrada!')
            # Criar configuração do Asaas
            config_asaas = ConfiguracaoBoleto.objects.create(
                codigo_banco="461",
                nome_banco="Asaas I.P S.A",
                nome_beneficiario="FELIX REPRESENTACOES E COMERCIO LTDA",
                cnpj_beneficiario="41.449.198/0001-72",
                agencia="0001",
                conta="194116-2",
                convenio="ASAAS",
                carteira="1",
                ativo=True
            )
            self.stdout.write(f'   ✅ Configuração Asaas criada: ID {config_asaas.id}')

        # 3. Verificar configurações ativas
        self.stdout.write('\n3️⃣ CONFIGURAÇÕES ATIVAS:')
        configs_ativas = ConfiguracaoBoleto.objects.filter(ativo=True)
        for config in configs_ativas:
            self.stdout.write(f'   ID: {config.id}, Banco: {config.codigo_banco} ({config.nome_banco})')

        # 4. Verificar último boleto gerado
        self.stdout.write('\n4️⃣ ÚLTIMO BOLETO GERADO:')
        ultimo_boleto = BoletoGerado.objects.all().order_by('-id').first()
        if ultimo_boleto:
            self.stdout.write(f'   ID: {ultimo_boleto.id}')
            self.stdout.write(f'   Número: {ultimo_boleto.numero_boleto}')
            self.stdout.write(f'   Banco: {ultimo_boleto.configuracao.codigo_banco} ({ultimo_boleto.configuracao.nome_banco})')
            self.stdout.write(f'   Configuração ID: {ultimo_boleto.configuracao.id}')
            
            # Verificar se tem dados do Asaas
            cobranca = CobrancaAsaas.objects.filter(controle_financeiro=ultimo_boleto.controle_financeiro).first()
            if cobranca:
                self.stdout.write(f'   ✅ Tem dados do Asaas: {cobranca.asaas_id}')
            else:
                self.stdout.write(f'   ❌ NÃO tem dados do Asaas')

        # 5. CORREÇÃO AUTOMÁTICA
        self.stdout.write('\n5️⃣ APLICANDO CORREÇÕES:')

        # Desativar todas as configurações antigas
        configs_antigas = ConfiguracaoBoleto.objects.exclude(codigo_banco="461")
        for config in configs_antigas:
            config.ativo = False
            config.save()
            self.stdout.write(f'   ✅ Desativada configuração {config.id} ({config.nome_banco})')

        # Ativar configuração do Asaas
        if config_asaas:
            config_asaas.ativo = True
            config_asaas.save()
            self.stdout.write(f'   ✅ Ativada configuração Asaas {config_asaas.id}')

        self.stdout.write('\n🎉 CORREÇÃO CONCLUÍDA!')
        self.stdout.write('Agora o sistema usará apenas a API do Asaas para gerar boletos com PIX.')

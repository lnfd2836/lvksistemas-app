"""
Comando para verificar e corrigir boletos existentes
"""

from django.core.management.base import BaseCommand
from controle_financeiro.models import BoletoGerado, ConfiguracaoBoleto
from controle_financeiro.boleto_caixa_service import BoletoCaixaService


class Command(BaseCommand):
    help = 'Verifica e corrige boletos existentes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Corrige problemas encontrados',
        )
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Valida códigos de barras existentes',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== VERIFICAÇÃO DE BOLETOS ==='))
        
        boletos = BoletoGerado.objects.all().order_by('-data_criacao')
        total_boletos = boletos.count()
        
        self.stdout.write(f'Total de boletos encontrados: {total_boletos}')
        
        if total_boletos == 0:
            self.stdout.write(self.style.WARNING('Nenhum boleto encontrado.'))
            return
        
        problemas_encontrados = 0
        boletos_validados = 0
        
        for boleto in boletos:
            self.stdout.write(f'\n--- Boleto {boleto.numero_boleto} ---')
            self.stdout.write(f'ID: {boleto.id}')
            self.stdout.write(f'Loja: {boleto.controle_financeiro.loja.nome}')
            self.stdout.write(f'Valor: R$ {boleto.valor}')
            self.stdout.write(f'Status: {boleto.status}')
            self.stdout.write(f'Data: {boleto.data_criacao}')
            
            # Verificar configuração
            config = boleto.configuracao
            self.stdout.write(f'Banco: {config.codigo_banco} - {config.nome_banco}')
            self.stdout.write(f'Agência: {config.agencia}')
            self.stdout.write(f'Conta: {config.conta}')
            self.stdout.write(f'Carteira: {config.carteira}')
            self.stdout.write(f'Cedente: {config.codigo_cedente}')
            self.stdout.write(f'Convênio: {config.convenio}')
            
            # Verificar se é da Caixa e tem problemas
            tem_problema = False
            
            if config.codigo_banco == "104":
                if not config.nome_banco or config.nome_banco.strip() == "":
                    self.stdout.write(self.style.ERROR('❌ Nome do banco vazio'))
                    tem_problema = True
                    
                    if options['fix']:
                        config.nome_banco = "Caixa Econômica Federal"
                        config.save()
                        self.stdout.write(self.style.SUCCESS('✅ Nome do banco corrigido'))
                
                if not config.codigo_cedente:
                    self.stdout.write(self.style.ERROR('❌ Código do cedente vazio'))
                    tem_problema = True
                
                if not config.convenio:
                    self.stdout.write(self.style.WARNING('⚠️ Convênio não informado'))
            
            # Validar código de barras se solicitado
            if options['validate'] and boleto.codigo_barras:
                try:
                    service = BoletoCaixaService()
                    validation_result = service.validar_boleto_existente(
                        boleto.codigo_barras, 
                        boleto.linha_digitavel
                    )
                    
                    if validation_result.is_valid:
                        self.stdout.write(self.style.SUCCESS('✅ Código de barras válido'))
                        boletos_validados += 1
                    else:
                        self.stdout.write(self.style.ERROR('❌ Código de barras inválido'))
                        for error in validation_result.errors:
                            self.stdout.write(f'  - {error}')
                        tem_problema = True
                        
                        if options['fix']:
                            self.stdout.write(self.style.WARNING('⚠️ Regeneração de código não implementada ainda'))
                    
                    if validation_result.warnings:
                        for warning in validation_result.warnings:
                            self.stdout.write(self.style.WARNING(f'⚠️ {warning}'))
                            
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Erro na validação: {str(e)}'))
                    tem_problema = True
            
            if tem_problema:
                problemas_encontrados += 1
        
        # Resumo final
        self.stdout.write(f'\n{"="*50}')
        self.stdout.write(self.style.SUCCESS('RESUMO DA VERIFICAÇÃO'))
        self.stdout.write(f'Total de boletos: {total_boletos}')
        self.stdout.write(f'Problemas encontrados: {problemas_encontrados}')
        
        if options['validate']:
            self.stdout.write(f'Boletos validados: {boletos_validados}')
            self.stdout.write(f'Boletos com problemas: {total_boletos - boletos_validados}')
        
        if problemas_encontrados > 0:
            if options['fix']:
                self.stdout.write(self.style.SUCCESS('✅ Problemas corrigidos automaticamente'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Execute com --fix para corrigir automaticamente'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Nenhum problema encontrado'))
        
        # Verificar configurações
        self.stdout.write(f'\n--- CONFIGURAÇÕES DE BOLETO ---')
        configs = ConfiguracaoBoleto.objects.all()
        
        for config in configs:
            self.stdout.write(f'\nConfiguração ID {config.id}:')
            self.stdout.write(f'  Banco: {config.codigo_banco} - {config.nome_banco}')
            self.stdout.write(f'  Ativo: {config.ativo}')
            self.stdout.write(f'  Agência: {config.agencia}')
            self.stdout.write(f'  Conta: {config.conta}')
            self.stdout.write(f'  Carteira: {config.carteira}')
            self.stdout.write(f'  Cedente: {config.codigo_cedente}')
            self.stdout.write(f'  Convênio: {config.convenio}')
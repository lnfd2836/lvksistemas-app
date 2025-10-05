"""
Comando de gerenciamento para validar URLs do sistema
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from dashboard.utils.url_validator import URLValidator, log_url_validation_report


class Command(BaseCommand):
    help = 'Valida todas as URLs críticas do sistema'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Mostra relatório detalhado de validação',
        )
        
        parser.add_argument(
            '--log-only',
            action='store_true',
            help='Apenas registra no log, não imprime no console',
        )
    
    def handle(self, *args, **options):
        """Executa a validação de URLs"""
        
        if options['log_only']:
            # Apenas registra no log
            report = log_url_validation_report()
            if report:
                self.stdout.write(
                    self.style.SUCCESS('Relatório de validação registrado no log.')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Validação de URL desabilitada (DEBUG=False).')
                )
            return
        
        # Executar validação completa
        self.stdout.write('Iniciando validação de URLs...')
        
        try:
            report = URLValidator.generate_validation_report()
            
            # Mostrar resumo
            self.stdout.write(f"\n=== Resumo da Validação ===")
            self.stdout.write(f"Total de URLs testadas: {report['summary']['total_urls']}")
            
            if report['summary']['valid_urls'] > 0:
                self.stdout.write(
                    self.style.SUCCESS(f"URLs válidas: {report['summary']['valid_urls']}")
                )
            
            if report['summary']['invalid_urls'] > 0:
                self.stdout.write(
                    self.style.ERROR(f"URLs inválidas: {report['summary']['invalid_urls']}")
                )
            
            # Mostrar erros se houver
            if report['summary']['errors']:
                self.stdout.write(f"\n=== Erros Encontrados ===")
                for error in report['summary']['errors']:
                    self.stdout.write(
                        self.style.ERROR(f"❌ {error['url_name']}: {error['error']}")
                    )
            
            # Mostrar detalhes se solicitado
            if options['detailed']:
                self.show_detailed_report(report)
            
            # Resultado final
            if report['summary']['invalid_urls'] == 0:
                self.stdout.write(
                    self.style.SUCCESS('\n✅ Todas as URLs foram validadas com sucesso!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'\n❌ {report["summary"]["invalid_urls"]} URLs falharam na validação.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro durante a validação: {str(e)}')
            )
    
    def show_detailed_report(self, report):
        """Mostra relatório detalhado"""
        
        self.stdout.write(f"\n=== Relatório Detalhado ===")
        
        # URLs do Dashboard
        self.stdout.write(f"\n--- URLs do Dashboard ---")
        for url_name, result in report['dashboard_urls'].items():
            status = "✅" if result['valid'] else "❌"
            self.stdout.write(f"{status} {url_name}")
            
            if result['valid']:
                self.stdout.write(f"    URL: {result['result']}")
            else:
                self.stdout.write(f"    Erro: {result['result']}")
            
            if 'params' in result:
                self.stdout.write(f"    Parâmetros: {result['params']}")
        
        # URLs de Lojas
        self.stdout.write(f"\n--- URLs de Lojas ---")
        for url_name, result in report['loja_urls'].items():
            status = "✅" if result['valid'] else "❌"
            self.stdout.write(f"{status} {url_name}")
            
            if result['valid']:
                self.stdout.write(f"    URL: {result['result']}")
            else:
                self.stdout.write(f"    Erro: {result['result']}")
            
            if 'params' in result:
                self.stdout.write(f"    Parâmetros: {result['params']}")
    
    def handle_error(self, message):
        """Trata erros de forma consistente"""
        self.stdout.write(self.style.ERROR(f'ERRO: {message}'))
        return False
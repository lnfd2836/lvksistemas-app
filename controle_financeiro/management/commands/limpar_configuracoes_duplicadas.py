"""
Comando para limpar configurações de boleto duplicadas
"""

from django.core.management.base import BaseCommand
from controle_financeiro.models import ConfiguracaoBoleto


class Command(BaseCommand):
    help = 'Remove configurações de boleto duplicadas, mantendo apenas a mais recente'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostra o que seria removido, sem fazer alterações',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        self.stdout.write("=== LIMPEZA DE CONFIGURAÇÕES DUPLICADAS ===\n")
        
        # Buscar todas as configurações
        todas_configs = ConfiguracaoBoleto.objects.all().order_by('-data_criacao')
        
        if not todas_configs.exists():
            self.stdout.write(self.style.WARNING("Nenhuma configuração encontrada."))
            return
        
        # Agrupar por banco
        configs_por_banco = {}
        for config in todas_configs:
            banco = config.codigo_banco
            if banco not in configs_por_banco:
                configs_por_banco[banco] = []
            configs_por_banco[banco].append(config)
        
        total_removidas = 0
        
        for banco, configs in configs_por_banco.items():
            if len(configs) > 1:
                # Manter apenas a mais recente
                mais_recente = configs[0]  # Já ordenado por -data_criacao
                duplicadas = configs[1:]
                
                self.stdout.write(f"\n📋 Banco {banco}:")
                self.stdout.write(f"  ✅ Mantendo: ID {mais_recente.id} - {mais_recente.nome_banco} (criada em {mais_recente.data_criacao})")
                
                for config in duplicadas:
                    self.stdout.write(f"  ❌ Removendo: ID {config.id} - {config.nome_banco} (criada em {config.data_criacao})")
                    
                    if not dry_run:
                        config.delete()
                    
                    total_removidas += 1
                
                # Garantir que a mais recente está ativa
                if not dry_run:
                    mais_recente.ativo = True
                    mais_recente.save()
                    self.stdout.write(f"  ✅ Configuração ID {mais_recente.id} marcada como ativa")
            
            else:
                config = configs[0]
                self.stdout.write(f"\n📋 Banco {banco}:")
                self.stdout.write(f"  ✅ Única configuração: ID {config.id} - {config.nome_banco}")
                
                # Garantir que está ativa
                if not dry_run and not config.ativo:
                    config.ativo = True
                    config.save()
                    self.stdout.write(f"  ✅ Configuração ID {config.id} marcada como ativa")
        
        # Resumo
        self.stdout.write(f"\n{'='*50}")
        if dry_run:
            self.stdout.write(self.style.WARNING(f"DRY RUN: {total_removidas} configurações seriam removidas"))
            self.stdout.write("Execute sem --dry-run para aplicar as alterações")
        else:
            if total_removidas > 0:
                self.stdout.write(self.style.SUCCESS(f"✅ {total_removidas} configurações duplicadas removidas com sucesso!"))
            else:
                self.stdout.write(self.style.SUCCESS("✅ Nenhuma duplicata encontrada. Banco de dados limpo!"))
        
        self.stdout.write(f"{'='*50}")
        
        # Mostrar configurações finais
        configs_finais = ConfiguracaoBoleto.objects.all().order_by('-data_criacao')
        self.stdout.write(f"\n📊 CONFIGURAÇÕES FINAIS ({configs_finais.count()}):")
        
        for config in configs_finais:
            status = "🟢 ATIVA" if config.ativo else "🔴 INATIVA"
            self.stdout.write(f"  • ID {config.id}: {config.nome_banco} (Banco {config.codigo_banco}) - {status}")
        
        if not configs_finais.exists():
            self.stdout.write("  (Nenhuma configuração)")
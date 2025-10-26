"""
Comando Django para gerenciar middlewares de lojas
"""
from django.core.management.base import BaseCommand
from django.core.management import CommandError
from lojas.models import Loja
from lojas.middleware.gerador_middleware_loja import MiddlewareLojaGenerator


class Command(BaseCommand):
    help = 'Gerencia middlewares exclusivos de lojas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['criar', 'remover', 'listar', 'recriar'],
            help='Ação a ser executada'
        )
        parser.add_argument(
            '--loja-id',
            type=str,
            help='ID da loja específica'
        )
        parser.add_argument(
            '--todas',
            action='store_true',
            help='Aplicar ação a todas as lojas'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        loja_id = options.get('loja_id')
        todas = options.get('todas', False)
        
        generator = MiddlewareLojaGenerator()
        
        if action == 'criar':
            self._criar_middlewares(generator, loja_id, todas)
        elif action == 'remover':
            self._remover_middlewares(generator, loja_id, todas)
        elif action == 'listar':
            self._listar_middlewares()
        elif action == 'recriar':
            self._recriar_middlewares(generator, loja_id, todas)
    
    def _criar_middlewares(self, generator, loja_id, todas):
        """Cria middlewares"""
        if todas:
            lojas = Loja.objects.filter(status='ativa')
            self.stdout.write(f"Criando middlewares para {len(lojas)} lojas...")
            
            for loja in lojas:
                resultado = generator.gerar_middleware_loja(loja)
                if resultado['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ {loja.nome}: {resultado['middleware_class']}")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ {loja.nome}: {resultado['error']}")
                    )
        
        elif loja_id:
            try:
                loja = Loja.objects.get(id=loja_id)
                resultado = generator.gerar_middleware_loja(loja)
                
                if resultado['success']:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Middleware criado: {resultado['middleware_class']}")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(f"❌ Erro: {resultado['error']}")
                    )
            except Loja.DoesNotExist:
                raise CommandError(f"Loja com ID {loja_id} não encontrada")
        
        else:
            raise CommandError("Especifique --loja-id ou --todas")
    
    def _remover_middlewares(self, generator, loja_id, todas):
        """Remove middlewares"""
        if todas:
            lojas = Loja.objects.all()
            self.stdout.write(f"Removendo middlewares de {len(lojas)} lojas...")
            
            for loja in lojas:
                if generator.remover_middleware_loja(loja):
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ {loja.nome}: Middleware removido")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"⚠️  {loja.nome}: Middleware não encontrado")
                    )
        
        elif loja_id:
            try:
                loja = Loja.objects.get(id=loja_id)
                if generator.remover_middleware_loja(loja):
                    self.stdout.write(
                        self.style.SUCCESS("✅ Middleware removido")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING("⚠️  Middleware não encontrado")
                    )
            except Loja.DoesNotExist:
                raise CommandError(f"Loja com ID {loja_id} não encontrada")
        
        else:
            raise CommandError("Especifique --loja-id ou --todas")
    
    def _listar_middlewares(self):
        """Lista middlewares existentes"""
        import os
        import glob
        
        middleware_files = glob.glob('lojas/middleware/loja_*_middleware.py')
        
        if middleware_files:
            self.stdout.write("📋 Middlewares de lojas encontrados:")
            for file in middleware_files:
                self.stdout.write(f"  • {os.path.basename(file)}")
        else:
            self.stdout.write("❌ Nenhum middleware de loja encontrado")
    
    def _recriar_middlewares(self, generator, loja_id, todas):
        """Recria middlewares (remove e cria novamente)"""
        self.stdout.write("🔄 Recriando middlewares...")
        self._remover_middlewares(generator, loja_id, todas)
        self._criar_middlewares(generator, loja_id, todas)

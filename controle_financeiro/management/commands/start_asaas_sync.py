"""
Comando Django para iniciar a sincronização em tempo real com Asaas
"""

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import time
import signal
import sys

from controle_financeiro.asaas_sync_service import get_sync_service


class Command(BaseCommand):
    help = 'Inicia a sincronização em tempo real com a API do Asaas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=300,
            help='Intervalo entre sincronizações em segundos (padrão: 300)'
        )
        
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Executa como daemon (não bloqueia o terminal)'
        )
        
        parser.add_argument(
            '--stop',
            action='store_true',
            help='Para a sincronização em execução'
        )
        
        parser.add_argument(
            '--status',
            action='store_true',
            help='Mostra o status atual da sincronização'
        )
    
    def handle(self, *args, **options):
        sync_service = get_sync_service()
        
        # Mostrar status
        if options['status']:
            self.show_status(sync_service)
            return
        
        # Parar sincronização
        if options['stop']:
            self.stop_sync(sync_service)
            return
        
        # Iniciar sincronização
        interval = options['interval']
        daemon = options['daemon']
        
        self.start_sync(sync_service, interval, daemon)
    
    def show_status(self, sync_service):
        """Mostra o status atual da sincronização"""
        status = sync_service.get_sync_status()
        
        self.stdout.write(self.style.HTTP_INFO("=== STATUS DA SINCRONIZAÇÃO ASAAS ==="))
        
        if status['is_running']:
            self.stdout.write(
                self.style.SUCCESS(f"✅ Sincronização ATIVA (intervalo: {status['sync_interval']}s)")
            )
        else:
            self.stdout.write(
                self.style.ERROR("❌ Sincronização PARADA")
            )
        
        self.stdout.write(f"Thread ativa: {'Sim' if status['thread_alive'] else 'Não'}")
        
        if status['last_sync']:
            self.stdout.write(f"Última sincronização: {status['last_sync']}")
        else:
            self.stdout.write("Última sincronização: Nunca executada")
        
        # Estatísticas
        stats = status['stats']
        self.stdout.write("\n=== ESTATÍSTICAS ===")
        self.stdout.write(f"Total sincronizado: {stats['total_synced']}")
        self.stdout.write(f"Atualizações encontradas: {stats['updates_found']}")
        self.stdout.write(f"Erros: {stats['errors']}")
        
        if stats['last_error']:
            self.stdout.write(
                self.style.ERROR(f"Último erro: {stats['last_error']}")
            )
    
    def stop_sync(self, sync_service):
        """Para a sincronização"""
        self.stdout.write("Parando sincronização...")
        
        if sync_service.stop_real_time_sync():
            self.stdout.write(
                self.style.SUCCESS("✅ Sincronização parada com sucesso")
            )
        else:
            self.stdout.write(
                self.style.WARNING("⚠️ Sincronização não estava em execução")
            )
    
    def start_sync(self, sync_service, interval, daemon):
        """Inicia a sincronização"""
        self.stdout.write(f"Iniciando sincronização (intervalo: {interval}s)...")
        
        # Verificar se já está rodando
        if sync_service.is_running:
            self.stdout.write(
                self.style.WARNING("⚠️ Sincronização já está em execução")
            )
            return
        
        # Configurar handler para SIGINT (Ctrl+C)
        def signal_handler(sig, frame):
            self.stdout.write("\n\nParando sincronização...")
            sync_service.stop_real_time_sync()
            self.stdout.write(
                self.style.SUCCESS("✅ Sincronização parada")
            )
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        
        # Iniciar sincronização
        if sync_service.start_real_time_sync(interval):
            self.stdout.write(
                self.style.SUCCESS("✅ Sincronização iniciada com sucesso")
            )
            
            if daemon:
                self.stdout.write("Executando como daemon...")
                return
            
            # Modo interativo - mostrar status periodicamente
            self.stdout.write("Pressione Ctrl+C para parar\n")
            
            try:
                while sync_service.is_running:
                    time.sleep(30)  # Atualizar status a cada 30 segundos
                    
                    status = sync_service.get_sync_status()
                    stats = status['stats']
                    
                    self.stdout.write(
                        f"[{status['last_sync'] or 'Nunca'}] "
                        f"Sincronizado: {stats['total_synced']} | "
                        f"Atualizações: {stats['updates_found']} | "
                        f"Erros: {stats['errors']}"
                    )
                    
                    if stats['last_error']:
                        self.stdout.write(
                            self.style.ERROR(f"Último erro: {stats['last_error']}")
                        )
            
            except KeyboardInterrupt:
                self.stdout.write("\n\nParando sincronização...")
                sync_service.stop_real_time_sync()
                self.stdout.write(
                    self.style.SUCCESS("✅ Sincronização parada")
                )
        
        else:
            self.stdout.write(
                self.style.ERROR("❌ Erro ao iniciar sincronização")
            )
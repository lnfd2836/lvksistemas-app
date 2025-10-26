"""
Modelos para controle de sincronização persistente
"""
from django.db import models
from django.utils import timezone
import json


class SyncStatus(models.Model):
    """Modelo para armazenar o status da sincronização de forma persistente"""
    
    # Chave única para identificar o status (sempre 'main')
    key = models.CharField(max_length=10, default='main', unique=True)
    
    # Status da sincronização
    is_running = models.BooleanField(default=False)
    sync_interval = models.IntegerField(default=300)  # segundos
    
    # Timestamps
    last_sync = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    stopped_at = models.DateTimeField(null=True, blank=True)
    
    # Estatísticas em JSON
    stats_json = models.TextField(default='{}')
    
    # Controle
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Status de Sincronização"
        verbose_name_plural = "Status de Sincronização"
    
    def __str__(self):
        return f"Sincronização {'ATIVA' if self.is_running else 'PARADA'}"
    
    @property
    def stats(self):
        """Retorna as estatísticas como dict"""
        try:
            return json.loads(self.stats_json)
        except:
            return {
                'total_synced': 0,
                'updates_found': 0,
                'errors': 0,
                'last_error': None
            }
    
    @stats.setter
    def stats(self, value):
        """Define as estatísticas como JSON"""
        self.stats_json = json.dumps(value)
    
    def start_sync(self, interval=300):
        """Marca a sincronização como iniciada"""
        self.is_running = True
        self.sync_interval = interval
        self.started_at = timezone.now()
        self.stopped_at = None
        self.save()
    
    def stop_sync(self):
        """Marca a sincronização como parada"""
        self.is_running = False
        self.stopped_at = timezone.now()
        self.save()
    
    def update_last_sync(self):
        """Atualiza o timestamp da última sincronização"""
        self.last_sync = timezone.now()
        self.save()
    
    def update_stats(self, stats_dict):
        """Atualiza as estatísticas"""
        current_stats = self.stats
        current_stats.update(stats_dict)
        self.stats = current_stats
        self.save()
    
    @classmethod
    def get_current(cls):
        """Obtém ou cria o status atual"""
        status, created = cls.objects.get_or_create(
            key='main',
            defaults={
                'is_running': False,
                'sync_interval': 300,
                'stats_json': json.dumps({
                    'total_synced': 0,
                    'updates_found': 0,
                    'errors': 0,
                    'last_error': None
                })
            }
        )
        return status
    
    def to_dict(self):
        """Converte para dicionário compatível com o serviço"""
        return {
            'is_running': self.is_running,
            'sync_interval': self.sync_interval,
            'last_sync': self.last_sync,
            'stats': self.stats,
            'thread_alive': False  # Sempre False no Heroku
        }
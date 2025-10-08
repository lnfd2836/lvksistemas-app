"""
Configuração do Celery para tarefas assíncronas
"""
import os
from celery import Celery

# Configura o Django settings module para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lojad.settings')

app = Celery('lojad')

# Configura o Celery usando as configurações do Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descobre tarefas em todos os apps Django
app.autodiscover_tasks()

# Configurações específicas do Celery
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Tarefas periódicas
app.conf.beat_schedule = {
    'backup-diario': {
        'task': 'lojas.tasks.backup_diario',
        'schedule': 86400.0,  # 24 horas
    },
    'otimizar-bancos': {
        'task': 'lojas.tasks.otimizar_bancos',
        'schedule': 604800.0,  # 7 dias
    },
    'limpar-logs-antigos': {
        'task': 'lojas.tasks.limpar_logs_antigos',
        'schedule': 2592000.0,  # 30 dias
    },
    # Tarefas financeiras
    'rotinas-financeiras-diarias': {
        'task': 'controle_financeiro.tasks.executar_rotinas_financeiras_diarias',
        'schedule': 86400.0,  # 24 horas - executa diariamente
        'options': {
            'expires': 3600,  # Expira em 1 hora se não executar
        }
    },
    'gerar-boletos-automaticos': {
        'task': 'controle_financeiro.tasks.gerar_boletos_automaticos_task',
        'schedule': 43200.0,  # 12 horas - executa 2x por dia
        'args': (10,),  # 10 dias de antecedência
        'options': {
            'expires': 1800,  # Expira em 30 minutos se não executar
        }
    },
    'verificar-boletos-vencidos': {
        'task': 'controle_financeiro.tasks.verificar_boletos_vencidos_task',
        'schedule': 21600.0,  # 6 horas - executa 4x por dia
        'options': {
            'expires': 900,  # Expira em 15 minutos se não executar
        }
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')







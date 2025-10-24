"""
Configuração do Celery para sincronização automática com Asaas
"""

from celery.schedules import crontab

# Configurações de tasks periódicas para sincronização Asaas
CELERY_BEAT_SCHEDULE = {
    # Sincronização contínua (a cada 5 minutos)
    'sync-asaas-charges': {
        'task': 'controle_financeiro.tasks.sync_asaas_charges_task',
        'schedule': crontab(minute='*/5'),  # A cada 5 minutos
        'options': {
            'expires': 240,  # Expira em 4 minutos
            'retry': True,
            'retry_policy': {
                'max_retries': 3,
                'interval_start': 0,
                'interval_step': 0.2,
                'interval_max': 0.2,
            }
        }
    },
    
    # Monitoramento de pagamentos (a cada 2 minutos)
    'monitor-asaas-payments': {
        'task': 'controle_financeiro.tasks.monitor_asaas_payments_task',
        'schedule': crontab(minute='*/2'),  # A cada 2 minutos
        'options': {
            'expires': 90,  # Expira em 1.5 minutos
            'retry': True,
            'retry_policy': {
                'max_retries': 2,
                'interval_start': 0,
                'interval_step': 0.1,
                'interval_max': 0.1,
            }
        }
    },
    
    # Rotinas financeiras diárias (todo dia às 6:00)
    'daily-financial-routines': {
        'task': 'controle_financeiro.tasks.executar_rotinas_financeiras_diarias',
        'schedule': crontab(hour=6, minute=0),  # 06:00 todos os dias
        'options': {
            'expires': 3600,  # Expira em 1 hora
            'retry': True,
            'retry_policy': {
                'max_retries': 3,
                'interval_start': 0,
                'interval_step': 60,
                'interval_max': 300,
            }
        }
    },
    
    # Verificação de vencimentos (todo dia às 8:00)
    'check-due-dates': {
        'task': 'controle_financeiro.tasks.verificar_vencimentos_task',
        'schedule': crontab(hour=8, minute=0),  # 08:00 todos os dias
        'options': {
            'expires': 1800,  # Expira em 30 minutos
        }
    },
    
    # Limpeza de dados antigos (toda segunda-feira às 2:00)
    'cleanup-old-sync-data': {
        'task': 'controle_financeiro.tasks.cleanup_old_sync_data_task',
        'schedule': crontab(hour=2, minute=0, day_of_week=1),  # Segunda-feira às 02:00
        'options': {
            'expires': 7200,  # Expira em 2 horas
        }
    },
    
    # Rotinas contínuas (a cada 5 minutos) - backup da sincronização principal
    'continuous-routines': {
        'task': 'controle_financeiro.tasks.executar_rotinas_continuas',
        'schedule': crontab(minute='*/5'),  # A cada 5 minutos
        'options': {
            'expires': 240,  # Expira em 4 minutos
            'retry': True,
            'retry_policy': {
                'max_retries': 2,
                'interval_start': 0,
                'interval_step': 30,
                'interval_max': 60,
            }
        }
    },
}

# Configurações específicas para tasks de sincronização
CELERY_TASK_ROUTES = {
    'controle_financeiro.tasks.sync_asaas_charges_task': {'queue': 'sync'},
    'controle_financeiro.tasks.sync_single_asaas_charge_task': {'queue': 'sync'},
    'controle_financeiro.tasks.monitor_asaas_payments_task': {'queue': 'sync'},
    'controle_financeiro.tasks.executar_rotinas_continuas': {'queue': 'sync'},
    'controle_financeiro.tasks.executar_rotinas_financeiras_diarias': {'queue': 'financial'},
    'controle_financeiro.tasks.cleanup_old_sync_data_task': {'queue': 'maintenance'},
}

# Configurações de retry para tasks críticas
CELERY_TASK_ANNOTATIONS = {
    'controle_financeiro.tasks.sync_asaas_charges_task': {
        'rate_limit': '10/m',  # Máximo 10 por minuto
        'time_limit': 300,     # Timeout de 5 minutos
        'soft_time_limit': 240, # Soft timeout de 4 minutos
    },
    'controle_financeiro.tasks.monitor_asaas_payments_task': {
        'rate_limit': '30/m',  # Máximo 30 por minuto
        'time_limit': 120,     # Timeout de 2 minutos
        'soft_time_limit': 90, # Soft timeout de 1.5 minutos
    },
    'controle_financeiro.tasks.sync_single_asaas_charge_task': {
        'rate_limit': '60/m',  # Máximo 60 por minuto
        'time_limit': 60,      # Timeout de 1 minuto
        'soft_time_limit': 45, # Soft timeout de 45 segundos
    },
}

# Configuração de filas
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_QUEUES = {
    'default': {
        'exchange': 'default',
        'exchange_type': 'direct',
        'routing_key': 'default',
    },
    'sync': {
        'exchange': 'sync',
        'exchange_type': 'direct',
        'routing_key': 'sync',
    },
    'financial': {
        'exchange': 'financial',
        'exchange_type': 'direct',
        'routing_key': 'financial',
    },
    'maintenance': {
        'exchange': 'maintenance',
        'exchange_type': 'direct',
        'routing_key': 'maintenance',
    },
}

# Configurações de monitoramento
CELERY_SEND_TASK_EVENTS = True
CELERY_TASK_SEND_SENT_EVENT = True

# Configurações de resultado
CELERY_RESULT_EXPIRES = 3600  # Resultados expiram em 1 hora
CELERY_TASK_RESULT_EXPIRES = 3600

# Configurações de worker
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Processar uma task por vez
CELERY_TASK_ACKS_LATE = True  # Confirmar apenas após conclusão
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000  # Reiniciar worker após 1000 tasks

def get_celery_config():
    """
    Retorna a configuração completa do Celery para sincronização
    """
    return {
        'beat_schedule': CELERY_BEAT_SCHEDULE,
        'task_routes': CELERY_TASK_ROUTES,
        'task_annotations': CELERY_TASK_ANNOTATIONS,
        'task_default_queue': CELERY_TASK_DEFAULT_QUEUE,
        'task_queues': CELERY_TASK_QUEUES,
        'send_task_events': CELERY_SEND_TASK_EVENTS,
        'task_send_sent_event': CELERY_TASK_SEND_SENT_EVENT,
        'result_expires': CELERY_RESULT_EXPIRES,
        'task_result_expires': CELERY_TASK_RESULT_EXPIRES,
        'worker_prefetch_multiplier': CELERY_WORKER_PREFETCH_MULTIPLIER,
        'task_acks_late': CELERY_TASK_ACKS_LATE,
        'worker_max_tasks_per_child': CELERY_WORKER_MAX_TASKS_PER_CHILD,
    }


def setup_celery_for_sync(celery_app):
    """
    Configura uma instância do Celery para sincronização
    
    Args:
        celery_app: Instância do Celery
    """
    config = get_celery_config()
    celery_app.conf.update(config)
    
    return celery_app
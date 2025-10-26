web: gunicorn lojad.wsgi --log-file -
worker: celery -A lojad worker --loglevel=info
beat: celery -A lojad beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler

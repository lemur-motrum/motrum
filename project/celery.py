import os
import sys

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
app = Celery('project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'current_rate': {
        'task': 'apps.core.tasks.get_currency',
        'schedule': crontab(minute='*/2'),
    },
    'specification_stop': {
        'task': 'apps.specification.tasks.specification_date_stop',
        'schedule': crontab(minute='*/2'),
    },
}
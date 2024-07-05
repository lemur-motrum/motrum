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
        'schedule': crontab(minute=20, hour=11),
    },
    'specification_stop': {
        'task': 'apps.specification.tasks.specification_date_stop',
        'schedule': crontab(minute=30, hour=11),
    },
    'add_iek': {
        'task': 'apps.supplier.tasks.add_iek',
        'schedule': crontab(minute=00, hour=12),
    },
    'add_veda': {
        'task': 'apps.supplier.tasks.add_veda',
        'schedule': crontab(minute=00, hour=11),
    },
    'add_prompower': {
        'task': 'apps.supplier.tasks.add_prompower',
        'schedule': crontab(minute=00, hour=10),
    },
}

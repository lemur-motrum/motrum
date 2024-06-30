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
        'schedule': crontab(minute="*/3"),
    },
    'specification_stop': {
        'task': 'apps.specification.tasks.specification_date_stop',
        'schedule': crontab(hour=0 , minute=15 ),
    },
    'add_iek': {
        'task': 'apps.supplier.tasks.add_iek',
        'schedule': crontab(hour=3,minute=0 ),
    },
    'add_veda': {
        'task': 'apps.supplier.tasks.add_veda',
        'schedule': crontab(hour=1, minute=0 ),
    },
    'add_prompower': {
        'task': 'apps.supplier.tasks.add_prompower',
        'schedule': crontab(hour=14, minute=0 ),
    },
}

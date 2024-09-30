import os
import sys

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
app = Celery('project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {

    'year_holidays': {
        'task': 'apps.core.tasks.get_year_holiday',
        'schedule': crontab(minute=3, hour=0, day_of_month=1),
    },
    'current_rate': {
        'task': 'apps.core.tasks.get_currency',
        'schedule': crontab(minute=10, hour=0),
    },
    'specification_stop': {
        'task': 'apps.specification.tasks.specification_date_stop',
        'schedule': crontab(minute=20, hour=0),
    },
    'add_iek': {
        'task': 'apps.supplier.tasks.add_iek',
        'schedule': crontab(minute=00, hour=3),
    },
    'add_veda': {
        'task': 'apps.supplier.tasks.add_veda',
        'schedule': crontab(minute=00, hour=2),
    },
    'add_prompower': {
        'task': 'apps.supplier.tasks.add_prompower',
        'schedule': crontab(minute=00, hour=1),
    },
    # таски днем повторы для теста
    
    # 'current_rate2': {
    #     'task': 'apps.core.tasks.get_currency',
    #     'schedule': crontab(minute=10, hour=12),
    # },
    # 'specification_stop2': {
    #     'task': 'apps.specification.tasks.specification_date_stop',
    #     'schedule': crontab(minute=20, hour=12),
    # },
    'add_iek3': {
        'task': 'apps.supplier.tasks.add_iek',
        'schedule': crontab(minute=45, hour=11),
    },
    'add_iek2': {
        'task': 'apps.supplier.tasks.add_iek',
        'schedule': crontab(minute=00, hour=15),
    },
    # 'add_veda2': {
    #     'task': 'apps.supplier.tasks.add_veda',
    #     'schedule': crontab(minute=00, hour=14),
    # },
    # 'add_prompower2': {
    #     'task': 'apps.supplier.tasks.add_prompower',
    #     'schedule': crontab(minute=00, hour=13),
    # },
    # 'add_iek3': {
    #     'task': 'apps.supplier.tasks.add_iek',
    #     'schedule': crontab(minute=00, hour=9),
    # },
}

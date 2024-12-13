import os
import sys

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
app = Celery('project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    #таски битрикс
    # 'get_status_order_bx': {
    #     'task': 'apps.core.tasks.get_status_order_bx',
    #     'schedule': crontab(minute=0, hour='6-21'),
    # },
    
    #таски ночные для обновления окт
    'counter_bill_new_year': {
        'task': 'apps.core.tasks.counter_bill_new_year',
        'schedule': crontab(minute=45, hour=0, day_of_month=1, month_of_year=1),
    },
    'year_holidays': {
        'task': 'apps.core.tasks.get_year_holiday',
        'schedule': crontab(minute=3, hour=0, day_of_month=1),
    },
    'current_rate': {
        'task': 'apps.core.tasks.get_currency',
        'schedule': crontab(minute=10, hour=0),
    },
    # 'specification_stop': {
    #     'task': 'apps.specification.tasks.specification_date_stop',
    #     'schedule': crontab(minute=20, hour=0),
    # },
    # 'bill_stop': {
    #     'task': 'apps.specification.tasks.bill_date_stop',
    #     'schedule': crontab(minute=40, hour=0),
    # },
    'add_iek': {
        'task': 'apps.supplier.tasks.add_iek',
        'schedule': crontab(minute=30, hour=0),
    },
    'add_veda': {
        'task': 'apps.supplier.tasks.add_veda',
        'schedule': crontab(minute=00, hour=3),
    },
    'add_prompower': {
        'task': 'apps.supplier.tasks.add_prompower',
        'schedule': crontab(minute=00, hour=2),
    },
   
}

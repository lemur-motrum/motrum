import os
import sys

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
app = Celery("project")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    # ТАСКИ битрикс
    # статусы битрикс заказов ежедневно
    'get_status_order_bx': {
        'task': 'apps.core.tasks.get_status_order_bx',
        'schedule': crontab(minute=0, hour='6-21'),
    },
    # получение менеджеров клиентов ежедневно
    'get_manager_info_bx': {
        'task': 'apps.core.tasks.get_manager_info_bx',
        'schedule': crontab(minute=00, hour=22),
    },
    # уведомления о повышения цен на товары и курсов ежедневно
    'add_currency_check_bx': {
        'task': 'apps.core.tasks.get_curr_price_check_bx',
        'schedule': crontab(minute=00, hour=5),
    },
    
    # ТАСКИ ночные для обновления окт ежедневные
    # курсы валют
    "current_rate": {
        "task": "apps.core.tasks.get_currency",
        "schedule": crontab(minute=10, hour=0),
    },
    # курсы валют проверка отсутствующих дат 
    "current_rate_old": {
        "task": "apps.core.tasks.get_currency_old",
        "schedule": crontab(minute=15, hour=0),
    },
    # проверка целостности изображений каталога
    "image_check": {
        "task": "apps.core.tasks.image_error_check_in",
        "schedule": crontab(minute=20, hour=0),
    },
    # # получение апи товаров иек
    "add_iek": {
        "task": "apps.supplier.tasks.add_iek",
        "schedule": crontab(minute=40, hour=0),
    },
    # получение апи товаров веда
    "add_veda": {
        "task": "apps.supplier.tasks.add_veda",
        "schedule": crontab(minute=00, hour=3),
    },
    # получение апи товаров промповер
    "add_prompower": {
        "task": "apps.supplier.tasks.add_prompower",
        "schedule": crontab(minute=00, hour=2),
    },
    # получение апи товаров промповер
    "add_unimat": {
        "task": "apps.supplier.tasks.add_unimat",
        "schedule": crontab(minute=45, hour=2),
    },
    # 'specification_stop': {
    #     'task': 'apps.specification.tasks.specification_date_stop',
    #     'schedule': crontab(minute=20, hour=0),
    # },
    # 'bill_stop': {
    #     'task': 'apps.specification.tasks.bill_date_stop',
    #     'schedule': crontab(minute=40, hour=0),
    # },
    # ТАСКИ раз в неделю
    # "iek_individual": {
    #     "task": "apps.supplier.tasks.add_iek_individual",
    #     "schedule": crontab(minute=3, hour=0, day_of_week=1),
    # },
    "vacancy_file_delite_week": {
        "task": "apps.core.tasks.vacancy_file_delite",
        "schedule": crontab(minute=22, hour=0, day_of_week=6),
    },
    
    # ТАСКИ ежемесячные
    # расписание рабочих дней этого года + в 12 месяц берет на след год
    "year_holidays": {
        "task": "apps.core.tasks.get_year_holiday",
        "schedule": crontab(minute=3, hour=0, day_of_month=1),
    },
    "nomenk_file_delite_month": {
        "task": "apps.core.tasks.nomenk_file_delite",
        "schedule": crontab(minute=14, hour=0, day_of_month=1),
    },
    "up_skafy": {
        "task": "apps.core.tasks.up_int_task_skafy",
        "schedule": crontab(minute=10, hour=0, day_of_month=1),
    },
    
    # ТАСКИ раз  в год
    # обнуление счетчиков счетов
    "counter_bill_new_year": {
        "task": "apps.core.tasks.counter_bill_new_year",
        "schedule": crontab(minute=45, hour=0, day_of_month=1, month_of_year=1),
    },
    # # обновить битые доки промповер
    # "add_prompower_new_doc": {
    #     "task": "apps.supplier.tasks.add_prompower_new_doc",
    #     "schedule": crontab(0, 0, day_of_month=8, month_of_year=4),
    # },
    # # обновить битые доки промповер
    "add_prompower_name_doc": {
        "task": "apps.supplier.tasks.add_prompower_name_doc",
        "schedule": crontab(0, 0, day_of_month=17, month_of_year=7),
    },
}

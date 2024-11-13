import datetime
from apps.client.models import Order
from apps.logs.utils import error_alert
from apps.specification.models import Specification
from project.celery import app
from django.db.models import Prefetch, OuterRef


@app.task(
    bind=True,
    max_retries=10,
)
def specification_date_stop(self):
    try:
        specification = Specification.objects.filter(tag_stop=True,number__isnull=False)

        for specification_item in specification:
            now = datetime.date.today()
            date = specification_item.date_stop

            if now >= date:
                specification_item.tag_stop = False
                specification_item._change_reason = "Автоматическое"
                specification_item.save()
                order = Order.objects.filter(specification=specification_item).update(status="CANCELED")

                
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            error = "file_api_error"
            location = "Отслеживание дат спецификаций"

            info = f"Отслеживание дат спецификаций не удалось"
            e = error_alert(error, location, info)
        self.retry(exc=exc, countdown=5)
        
        
@app.task(
    bind=True,
    max_retries=10,
)
def bill_date_stop(self):
    try:
        bill = Order.objects.filter(bill_sum__isnull=False, bill_sum_paid=0,date_completed__isnull=True).exclude(status="CANCELED")

        for bill_item in bill:
            print(bill)
            now = datetime.date.today()
            date = bill_item.bill_date_stop

            if now >= date:
                bill_item.bill_tag_stop = False
                bill_item._change_reason = "Автоматическое"
                bill_item.status = "CANCELED"
                bill_item.save()

                
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            error = "file_api_error"
            location = "Отслеживание дат счетов"

            info = f"Отслеживание дат счетов не удалось"
            e = error_alert(error, location, info)
        self.retry(exc=exc, countdown=5)        

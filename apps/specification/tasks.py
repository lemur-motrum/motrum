import datetime
from apps.logs.utils import error_alert
from apps.specification.models import Specification
from project.celery import app


@app.task(
    bind=True,
    max_retries=10,
)
def specification_date_stop(self):
    try:
        specification = Specification.objects.filter(tag_stop=True)
        for specification_item in specification:
            now = datetime.date.today()
            date = specification_item.date_stop

            if now >= date:
                specification_item.tag_stop = False
                specification_item.save()
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            error = "file_api_error"
            location = "Отслеживание дат спецификаций"

            info = f"Отслеживание дат спецификаций не удалось"
            e = error_alert(error, location, info)
        self.retry(exc=exc, countdown=5)

import datetime
from apps.specification.models import  Specification
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
        self.retry(exc=exc, countdown=5)
            
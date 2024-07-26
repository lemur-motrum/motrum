from requests import JSONDecodeError
from apps.logs.utils import error_alert
from apps.supplier.get_utils.iek import iek_api
from apps.supplier.get_utils.prompower import prompower_api
from apps.supplier.get_utils.veda import veda_api
from project.celery import app
from celery.exceptions import MaxRetriesExceededError, Reject, Retry


@app.task(
    bind=True,
    max_retries=10,
)
def add_iek(self):
    try:
        iek_api()
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            error = "file_api_error"
            location = "Связь с сервером ИЕК"

            info = f"Нет связи с сервером ИЕК "
            e = error_alert(error, location, info)

        self.retry(exc=exc, countdown=600)



@app.task(
    bind=True,
    max_retries=10,
)
def add_veda(self):
    try:
        veda_api()
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            error = "file_api_error"
            location = "Связь с сервером VEDA"

            info = f"Нет связи с сервером VEDA "
            e = error_alert(error, location, info)
        self.retry(exc=exc, countdown=600)


@app.task(
    bind=True,
    max_retries=10,
)
def add_prompower(self):
    try:
        prompower_api()
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            error = "file_api_error"
            location = "Связь с сервером Prompower"

            info = f"Нет связи с сервером Prompower "
            e = error_alert(error, location, info)
        self.retry(exc=exc, countdown=600)

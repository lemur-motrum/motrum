from requests import JSONDecodeError
from apps.core.utils import add_new_photo_adress_prompower
from apps.logs.utils import error_alert
from apps.supplier.get_utils.iek import get_iek_stock, iek_api, update_prod_iek_in_okt
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
            get_iek_stock()
        self.retry(exc=exc, countdown=600)
        
        
@app.task(
    bind=True,
    max_retries=10,
)
def add_iek_individual(self):
    try:
        update_prod_iek_in_okt()
        # update_prod_iek_in_okt()
        # get_iek_stock()
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            error = "file_api_error"
            location = "Связь с сервером ИЕК еженедельный"

            info = f"Нет связи с сервером ИЕК еженедельный"
            e = error_alert(error, location, info)
            get_iek_stock()
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


@app.task(
    bind=True,
    max_retries=10,
)
def add_prompower_new_doc(self):
    try:
        add_new_photo_adress_prompower()
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            error = "file_api_error"
            location = "Связь с сервером Prompower"

            info = f"Нет связи с сервером Prompower "
            e = error_alert(error, location, info)

        self.retry(exc=exc, countdown=600)


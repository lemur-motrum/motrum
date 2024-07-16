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
            if exc == MaxRetriesExceededError or exc == JSONDecodeError:
                error = "file_api_error"
                location = "Связь с сервером ИЕК"
          
                info = f"Нет связи с сервером ИЕК"
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
            self.retry(exc=exc, countdown=600) 



@app.task(
    bind=True,
    max_retries=10,
)
def add_prompower(self):
    try:
        prompower_api()
    except Exception as exc:
            self.retry(exc=exc, countdown=600)                                  
            
      
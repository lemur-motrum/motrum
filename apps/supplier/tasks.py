from apps.supplier.get_utils.iek import iek_api
from apps.supplier.get_utils.prompower import prompower_api
from apps.supplier.get_utils.veda import veda_api
from project.celery import app

@app.task(
    bind=True,
    max_retries=10,
)
def add_iek(self):
    try:
        
        iek_api()
    except Exception as exc:
            self.retry(exc=exc, countdown=5) 
            
@app.task(
    bind=True,
    max_retries=10,
)
def add_veda(self):
    try:
        veda_api()
    except Exception as exc:
            self.retry(exc=exc, countdown=5) 



@app.task(
    bind=True,
    max_retries=10,
)
def add_prompower(self):
    try:
        prompower_api()
    except Exception as exc:
            self.retry(exc=exc, countdown=5)                                  
            
      
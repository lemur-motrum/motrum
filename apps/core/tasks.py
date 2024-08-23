import datetime
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from xml.etree import ElementTree, ElementInclude
from simple_history.utils import update_change_reason

from apps.core.models import CalendarHoliday, Currency
from apps.logs.utils import error_alert
from apps.product.models import CurrencyRate, Price
from apps.specification.models import ProductSpecification, Specification
from project.celery import app


@app.task(
    bind=True,
    max_retries=10,
)
def get_currency(self):
  
    try:
        del_currency()
        currency_list = Currency.objects.exclude(words_code="RUB")
        resp = "https://www.cbr.ru/scripts/XML_daily.asp"
        response = urlopen(resp)
        item = ET.parse(response)
        root = item.getroot()
        ElementInclude.include(root)
        date = datetime.datetime.now()
        for current in currency_list:
            current_world_code = current.words_code
            value = item.findtext(f".//Valute[CharCode='{current_world_code}']/Value")
            vunit_rate = item.findtext(
                f".//Valute[CharCode='{current_world_code}']/VunitRate"
            )
            count = item.findtext(f".//Valute[CharCode='{current_world_code}']/Nominal")
            
            v = float(value.replace(",", "."))
            vi = float(vunit_rate.replace(",", "."))

            now_rate = CurrencyRate.objects.get_or_create(
                currency=current ,
                date=date,
                defaults={"value": v, "vunit_rate": vi, "count": int(count)},
            )
            update_currency_price(current, current_world_code)
            currency_chek(current, now_rate[0])

    except Exception as exc:
        if self.request.retries >= self.max_retries:
            error = "file_api_error"
            location = "Обновление валют"
            info = f"Обновление валют и валютных цен не удалось"
            e = error_alert(error, location, info)
        self.retry(exc=exc, countdown=160)


# удаление старых курсов
def del_currency():
   
    now = datetime.datetime.now()
    three_days = datetime.timedelta(3)
    in_three_days = now - three_days
    data = in_three_days.strftime("%Y-%m-%d")
    CurrencyRate.objects.filter(date__lt=data).delete()


# обновление валютных цен у всех продуктов
def update_currency_price(currency, current_world_code):
    products = Price.objects.filter(currency=currency)
    for product in products:
        price = Price.objects.get(id=product.id)
        price._change_reason = 'Автоматическое'
        price.save()
        # update_change_reason(price, "Автоматическое")        


# проверка на увелисеие курса на 3% -если да отмерка спецификации не действительны
def currency_chek(current, now_rate):

    old_rate = CurrencyRate.objects.filter(
        currency=current,
    ).earliest("date")
    old_rate_count = old_rate.vunit_rate
    new_rate_count = now_rate.vunit_rate
    difference_count = old_rate_count - new_rate_count

    count_percent = old_rate_count / 100 * 3
    print(difference_count)
    print(count_percent)
    if difference_count > count_percent:
       
        try:
            product_specification = ProductSpecification.objects.filter(product_currency=now_rate.currency, specification__tag_stop=True).values('specification')
            for prod in product_specification:
                specification = Specification.objects.get(
                tag_stop=True, id=prod["specification"]
            )
                specification.tag_stop = False
                specification.save()
                # update_change_reason(specification, "Автоматическое") 
                  
        except  ProductSpecification.DoesNotExist:
            pass


@app.task(
    bind=True,
    max_retries=10,
)
def get_year_holiday(self):
    try:
        import json
        import requests
        year_date = datetime.datetime.now().year
        year = str(year_date)
        url = (
                "https://raw.githubusercontent.com/d10xa/holidays-calendar/master/json/consultant"
                + year
                + ".json"
            )
        r = requests.get(url)
        holidays_dict = r.json()
        
        try:
            data_bd = CalendarHoliday.objects.get(year=year)
            data_bd.json_date = holidays_dict
            data_bd.save()
    
        except CalendarHoliday.DoesNotExist:

            data_bd = CalendarHoliday(year=year, json_date=holidays_dict)
            data_bd.save()
            
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            error = "file_api_error"
            location = "Получение производственного календаря"

            info = f"Получение производственного календаря не удалось"
            e = error_alert(error, location, info)
        self.retry(exc=exc, countdown=160)    
    

import datetime
from trace import Trace
from urllib.request import urlopen
import xml.etree.ElementTree as ET
from xml.etree import ElementTree, ElementInclude
from apps.core.bitrix_api import currency_check_bx, get_status_order
from simple_history.utils import update_change_reason

from apps.client.models import Order
from apps.core.models import BaseInfo, CalendarHoliday, Currency
from apps.core.utils import delete_everything_in_folder, image_error_check
from apps.logs.utils import error_alert
from apps.product.models import Cart, CurrencyRate, Price
from apps.specification.models import ProductSpecification, Specification
from project.celery import app
from django.db.models import Prefetch, OuterRef

from project.settings import MEDIA_ROOT


@app.task(
    bind=True,
    max_retries=10,
)
def get_currency(self):
    print("get_currency")
    try:
        # del_currency()
        currency_list = Currency.objects.exclude(words_code="RUB")
        resp = "https://www.cbr.ru/scripts/XML_daily.asp"
        response = urlopen(resp)
        item = ET.parse(response)
        root = item.getroot()
        ElementInclude.include(root)
        date = datetime.datetime.now()
        for current in currency_list:
            print(current)
            current_world_code = current.words_code
            value = item.findtext(f".//Valute[CharCode='{current_world_code}']/Value")
            vunit_rate = item.findtext(
                f".//Valute[CharCode='{current_world_code}']/VunitRate"
            )
            count = item.findtext(f".//Valute[CharCode='{current_world_code}']/Nominal")

            v = float(value.replace(",", "."))
            vi = float(vunit_rate.replace(",", "."))

            now_rate = CurrencyRate.objects.get_or_create(
                currency=current,
                date=date,
                defaults={"value": v, "vunit_rate": vi, "count": int(count)},
            )
            print(now_rate)
            update_currency_price(current, current_world_code)
            print(current, now_rate[0])
            # currency_chek(current, now_rate[0])

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
    CurrencyRate.objects.filter(date__lte=data).delete()


# обновление валютных цен у всех продуктов
def update_currency_price(currency, current_world_code):
    products = Price.objects.filter(currency=currency)
    for product in products:
        price = Price.objects.get(id=product.id)
        price._change_reason = "Автоматическое"
        price.save()
        # update_change_reason(price, "Автоматическое")


# проверка на увелисеие курса на 3% -если да отмерка спецификации не действительны
def currency_chek(current, now_rate):
    now = datetime.datetime.now()
    three_days = datetime.timedelta(3)
    in_three_days = now - three_days
    data_old = in_three_days.strftime("%Y-%m-%d")
    print(data_old)
    old_rate = CurrencyRate.objects.get(currency=current, date=data_old)
    print(old_rate)
    # old_rate = CurrencyRate.objects.filter(
    #     currency=current,
    # ).earliest("date")
    old_rate_count = old_rate.vunit_rate
    new_rate_count = now_rate.vunit_rate
    # difference_count = old_rate_count - new_rate_count
    difference_count = new_rate_count - old_rate_count

    count_percent = old_rate_count / 100 * 3
    print(difference_count, count_percent)
    if difference_count > count_percent:

        try:
            print(difference_count)

            product_specification = (
                ProductSpecification.objects.filter(
                    product_currency=now_rate.currency,
                )
                .exclude(specification__order__status__in=["CANCELED", "COMPLETED"])
                .distinct("specification__order")
                .values("specification", "specification__order")
                .exclude(specification__order=None)
            )
            print(product_specification)

            # product_specification = ProductSpecification.objects.filter(product_currency=now_rate.currency, specification__tag_stop=True).values('specification')
            # for prod in product_specification:
            #     specification = Specification.objects.get(
            #     tag_stop=True, id=prod["specification"]
            # )
            #     specification.tag_stop = False
            #     specification._change_reason = "Автоматическое"

            #     specification.save()
            #     try:
            #         order = Order.objects.get(specification=specification,date_completed__isnull=True,bill_sum__isnull=False,bill_tag_stop=True)
            #         order.tag_stop = False
            #         order.status = "CANCELED"
            #         order._change_reason = "Автоматическое"
            #     except Order.DoesNotExist:
            #          pass
        except ProductSpecification.DoesNotExist:
            pass


@app.task(
    bind=True,
    max_retries=10,
)
def get_year_holiday(self):
    try:
        import json
        import requests

        # year_date = datetime.datetime.now().year
        # year = str(year_date)

        if datetime.datetime.now().month == 12:
            year_date = datetime.datetime.now() + datetime.timedelta(days=367)
            year_date = year_date.year
        else:
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


# НЕ ИСПУЛЬЗУЮ  рабочие дня на след год(теперь внутри ежемесячной проверки берет за в )
@app.task(
    bind=True,
    max_retries=10,
)
def get_next_year_holiday(self):
    try:
        import json
        import requests

        if datetime.datetime.now().month == 12:
            year_date = datetime.datetime.now() + datetime.datetime.timedelta(days=367)
            year_date = year_date.year
        else:
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


# сброс сетчиков документов в начале года
@app.task(
    bind=True,
    max_retries=10,
)
def counter_bill_new_year(self):
    try:
        вase_info = BaseInfo.objects.filter().update(
            counter_bill=0, counter_bill_offer=0
        )
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            error = "file_api_error"
            location = "Обнуление счетчика счетов"

            info = f"Обнуление счетчика счетов"
            e = error_alert(error, location, info)
        self.retry(exc=exc, countdown=160)


# НЕ ИСПУЛЬЗУЮ
@app.task(
    bind=True,
    max_retries=10,
)
def del_void_cart(self):
    try:
        carts = (
            Cart.objects.prefetch_related(Prefetch("productcart_set"))
            .filter()
            .order_by("id")
        )
        print(carts)
        for cart in carts:
            print(cart)
            print(cart.productcart_set)
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            error = "file_api_error"
            location = "Удаление пустых корзин"

            info = f"Удаление пустых корзин"
            e = error_alert(error, location, info)
        self.retry(exc=exc, countdown=160)


# получение статусов б24 к сделкам
@app.task(
    bind=True,
    max_retries=1,
)
def get_status_order_bx(self):
    try:
        get_status_order()
    except Exception as exc:
        error = "file_api_error"
        location = f"получение в б24 статусов"

        info = f"получение в б24 статусов{exc}"
        e = error_alert(error, location, info)


# проверка и запись в Б24 курса валют и измеения цен на товары
@app.task(
    bind=True,
    max_retries=1,
)
def get_curr_price_check_bx(self):
    try:
        currency_check_bx()
    except Exception as exc:
        error = "file_api_error"
        location = f"отправка в б24 Критичные изменения цен и курса валют {exc}"

        info = f"отправка в б24 Критичные изменения цен и курса валют{exc}"
        e = error_alert(error, location, info)


# проверка битых изображений - удаление
@app.task(
    bind=True,
    max_retries=1,
)
def image_error_check_in(self):
    try:
        image_error_check()
    except Exception as exc:
        error = "file_api_error"
        location = f"удаление битых картинок {exc}"

        info = f"удаление битых картинок {exc}"
        e = error_alert(error, location, info)


# чистка папки с вакансиями
@app.task(
    bind=True,
    max_retries=1,
)
def vacancy_file_delite(self):
    try:
        folder_path = f"{MEDIA_ROOT}/documents/vacancy"

        delete_everything_in_folder(folder_path)

    except Exception as exc:
        error = "file_api_error"
        location = f"чистка папки с вакансиями {exc}"

        info = f"чистка папки с вакансиями {exc}"
        e = error_alert(error, location, info)

# чистка папки с 1c каталогами
@app.task(
    bind=True,
    max_retries=1,
)
def nomenk_file_delite(self):
    try:
        folder_path = f"{MEDIA_ROOT}/ones/nomenk"

        delete_everything_in_folder(folder_path)

    except Exception as exc:
        error = "file_api_error"
        location = f"чистка папки  с 1c каталогами {exc}"

        info = f"чистка папки  с 1c каталогами {exc}"
        e = error_alert(error, location, info)


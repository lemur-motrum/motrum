from datetime import datetime
import json

from django.http import Http404, JsonResponse
from requests import HTTPError
import requests
from apps.client.models import Order
from apps.core.bitrix_api import get_status_order
from apps.core.models import Currency
from apps.core.utils import send_requests
from apps.logs.utils import error_alert
from apps.product.models import CurrencyRate
from project.celery import app
from django.db.models import Prefetch, OuterRef


# @app.task(
#     bind=True,
#     max_retries=10,
# )
# def actual_info_order_product(self):
#     try:
#         data = {}
#         orders = []
#         currency = []
#         not_status = ["CANCELED", "COMPLETED"]
#         order = Order.objects.exclude(status__in=not_status)
#         for order_item in order:
#             order_product = (
#                 order_item.specification.productspecification_set.all().select_related(
#                     "product"
#                 )
#             )
#             order_data = {"bitrix_id": order_item.id_bitrix, "order_products": []}
#             for product in order_product:

#                 product_article_motrum = product.product.article
#                 product_article = product.product.article_supplier
#                 price_one_actual = product.product.price.rub_price_supplier

#                 prod = {
#                     "article_motrum": product_article_motrum,
#                     "article": product_article,
#                     "price_one_actual": price_one_actual,
#                 }
#                 order_data["order_products"].append(prod)

#             orders.append(order_data)
#         data["orders"] = orders

#         date_now = datetime.today()
#         currency_rate = CurrencyRate.objects.filter(date=date_now)
#         for currency_rate_item in currency_rate:
#             data_curr = {
#                 "currency_name": currency_rate_item.currency.words_code,
#                 "currency_rate": currency_rate_item.vunit_rate,
#                 "currency_date": currency_rate_item.date.strftime("%d.%m.%Y"),
#             }
#             currency.append(data_curr)

#         data["currency"] = currency
 
#         data = json.dumps(data)
#         url = "http://localhost:8000/api/v1/order/test/"
#         headers = {'Content-type': 'application/json'}
#         result_requests = send_requests(url,headers,data)
#         if result_requests  != 200:
#             raise Http404(f"http{result_requests}")
        

#     except Exception as exc:
       
#         if self.request.retries >= self.max_retries:
#             error = "file_api_error"
#             location = "отправка в б24 Критичные изменения цен и курса валют{exc}"
#             info = f"отправка в б24 Критичные изменения цен и курса валют{exc}"
#             e = error_alert(error, location, info)
#         self.retry(exc=exc, countdown=160)



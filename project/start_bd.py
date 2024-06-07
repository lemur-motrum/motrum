from django.contrib.auth.models import Group
from apps.core.models import Currency, CurrencyPercent, Vat
from apps.product.models import Lot
from apps.supplier.models import Supplier


def start_project_in_server():
    Currency.objects.create(name="Российский рубль",words_code="RUB",code=643)
    Currency.objects.create(name="	Китайский юань",words_code="CNY",code=156)
    
    Vat.objects.create(name="20",)
    
    CurrencyPercent.objects.create(percent=1.3)
    
    Lot.objects.create(name="набор",name_shorts="наб",slug="nabor")
    Lot.objects.create(name="комплект",name_shorts="комп",slug="komplekt")
    Lot.objects.create(name="штука",name_shorts="шт",slug="shtuka")
    
    Supplier.objects.create(name="PromPower",slug="prompower")
    Supplier.objects.create(name="EMAS",slug="EMAS")
    Supplier.objects.create(name="Авангард",slug="avangard")
    Supplier.objects.create(name="IEK",slug="iek")
    # Supplier.objects.create(name="",slug="")
    # Supplier.objects.create(name="",slug="")
    # Supplier.objects.create(name="",slug="")
    
    group = Group.objects.create(name="Базовый доступ")
    group = Group.objects.create(name="Доступ администрирования товаров")
    group = Group.objects.create(name="Доступ для загрузки каталогов поставщиков")
    group = Group.objects.create(name="Полный доступ")
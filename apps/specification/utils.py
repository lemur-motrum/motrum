import datetime
from apps.specification.models import Specification


def specification_date_stop():
    specification = Specification.objects.filter(tag_stop=False)
    for specification_item in specification:
        now = datetime.datetime.now()
        date = specification_item.date_stop
        if now == date:
            specification_item.tag_stop = True
            specification_item.save()
            
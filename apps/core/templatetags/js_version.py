from django import VERSION, template
from project.settings import IS_TESTING
import random

register = template.Library()


@register.simple_tag(takes_context=False)
def js_version():
    if IS_TESTING:
        ver = random.randint(0, 3124567)
    else:
        ver = VERSION
    return ver

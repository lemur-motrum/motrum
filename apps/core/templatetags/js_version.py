from django import template

register = template.Library()


@register.simple_tag(takes_context=False)
def js_version():
    ver = "1.1"
    return ver

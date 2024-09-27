from django import template

from apps.client.models import STATUS_ORDER


register = template.Library()

@register.filter
def quality(q):
    for choice in STATUS_ORDER:
        if choice[0] == q:
            return choice[1]
    return ''
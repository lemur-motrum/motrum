from django import template
from datetime import datetime

register = template.Library()


@register.inclusion_tag("core/includes/current_year.html", takes_context=False)
def current_year():
    year = datetime.now().year
    return {
        "year": year,
    }

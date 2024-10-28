from django import template
from datetime import datetime

register = template.Library()


@register.inclusion_tag("core/includes/overlay_compete_modal.html", takes_context=False)
def today():
    today = datetime.now().strftime("%Y-%m-%d")
    return {
        "today": today,
    }

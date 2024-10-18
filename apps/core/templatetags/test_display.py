from django import template
from project.settings import IS_TESTING

register = template.Library()


@register.inclusion_tag('core/base_okt.html', takes_context=True)
def test_display(context):
    if IS_TESTING:
        return f"style='display: none;'"
    else:
         return f""
    

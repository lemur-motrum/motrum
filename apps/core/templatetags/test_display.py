from django import template
from project.settings import IS_WEB

register = template.Library()


@register.simple_tag
def test_display():
    if IS_WEB :
        pass
    else:
        text = 'style=display:none;'
        return text
    
    

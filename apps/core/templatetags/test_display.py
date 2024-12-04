from django import template
from apps.user.models import AdminUser
from project.settings import IS_WEB

register = template.Library()


@register.simple_tag(takes_context=True)
def test_display(context):
    request = context['request']
    if request.user:
        user = AdminUser.objects.get(id=request.user.id).admin_type
        if user == "ALL":
            pass
        else:
            text = 'style=display:none;'
            return text
    else:
        text = 'style=display:none;'
        return text    
    # if IS_WEB :
    #     pass
    # else:
    #     text = 'style=display:none;'
    #     return text
    
    
    

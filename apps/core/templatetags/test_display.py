from django import template
from apps.user.models import AdminUser
from project.settings import IS_PROD, IS_TESTING, IS_WEB

register = template.Library()


@register.simple_tag(takes_context=True)
def test_display(context):
    pass
    if IS_TESTING:
        text = 'style=background-color:bisque;'
        return text
    else:
        pass
        
    #     request = context["request"]

    #     if request.user.id:
    #         if request.user.is_staff:
    #             user = AdminUser.objects.get(id=request.user.id).admin_type
    #             if user == "ALL":
    #                 pass
    #             else:
    #                 text = "style=display:none;"
    #                 return text
    #         else:
    #             text = "style=display:none;"
    #             return text
    #     else:
    #         text = "style=display:none;"
    #         return text

from django import template
from apps.user.models import AdminUser
from project.settings import IS_TESTING, IS_WEB

register = template.Library()


@register.simple_tag(takes_context=True)
def test_display(context):

    if IS_TESTING:
        pass
    else:
        request = context["request"]

        if request.user.id:
            if request.user.is_staff:
                user = AdminUser.objects.get(id=request.user.id).admin_type
                if user == "ALL":
                    pass
                else:
                    text = "style=display:none;"
                    return text
            else:
                text = "style=display:none;"
                return text
        else:
            text = "style=display:none;"
            return text

from django import template


register = template.Library()


@register.inclusion_tag('core/header/header_menu.html', takes_context=True)
def header_menu_url(context):
    return {
            'view_name': context.request.resolver_match.view_name,
            'namespace': context.request.resolver_match.namespace,
        }

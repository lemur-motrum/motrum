from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def is_active(context, *patterns):
    """
    Проверяет, начинается ли текущий путь с любым из указанных паттернов.
    Пример использования: {% is_active '/catalog' '/brand' as active %}
    """
    request = context.get('request')
    if not request:
        return False
    path = request.path
    for pattern in patterns:
        if path.startswith(pattern):
            return True
    return False 
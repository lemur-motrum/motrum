from django import template
register = template.Library()

@register.simple_tag
def get_verbose_field_name(instance, field_name, obj):
    """
    Returns verbose_name for a field.
    """

    return obj._meta.verbose_name.title()
from django import template

register = template.Library()


@register.filter
def number_space(value):

    try:
        num = "{0:,}".format(value).replace(",", " ")
        return num

    except ValueError:
        return value

from django import template

register = template.Library()

@register.filter
def  number_into_digits(value):
    num = "{0:,.2f}".format(value).replace(",", " ")
    return num
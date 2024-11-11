from django import template

register = template.Library()

@register.filter
def  number_into_digits(value):

    try:
        value = float(value)

        num = "{0:,.2f}".format(value).replace(",", " ").replace('.', ',')
        return num
    
    except ValueError:
        return value
       
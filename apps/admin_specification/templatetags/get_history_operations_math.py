from django import template

register = template.Library()


@register.simple_tag
def get_history_operations_math(value, valuenew):
    sum_operation = float(valuenew) - float(value)
    sum_operation = "{0:,.2f}".format(sum_operation).replace(",", " ").replace(".", ",")

    return sum_operation

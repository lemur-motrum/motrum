from django import template

register = template.Library()

@register.simple_tag
def  get_history_operations_math(value,valuenew):
    sum_operation = float(valuenew) - float(value)
    
    return sum_operation
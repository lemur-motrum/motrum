from django import template
from django.template import loader

register = template.Library()


@register.inclusion_tag('core/includes/js_templates.html', takes_context=False)
def js_templates():
    template_list = [
        {
            'module': 'catalog',
            'name': 'product-item',
            'template': 'product/includes/ajax_product_item.html',
        }
    ]

    for template_item in template_list:
        loaded_template = loader.get_template(template_item['template'])
        template_item['template'] = loaded_template.template.source

    return {
        'template_list': template_list,
    }

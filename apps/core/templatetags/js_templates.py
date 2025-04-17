from django import template
from django.template import loader

register = template.Library()


@register.inclusion_tag("core/includes/js_templates.html", takes_context=False)
def js_templates():
    template_list = [
        {
            "module": "catalog",
            "name": "product-item",
            "template": "product/includes/ajax_product_item.html",
        },
        {
            "module": "lk",
            "name": "order-item",
            "template": "client/includes/ajax_order_item.html",
        },
        {
            "module": "lk",
            "name": "document-item",
            "template": "client/includes/ajax_document_item.html",
        },
        {
            "module": "project",
            "name": "project-item",
            "template": "projects_web/includes/ajax_project_item.html",
        },
        {
            "module": "specification",
            "name": "specification-item",
            "template": "admin_specification/include/ajax_specification_item.html",
        },
        {
            "module": "admin-specif-search",
            "name": "search-specification-item",
            "template": "admin_specification/include/ajax_new_product_search_elem.html",
        },
        {
            "module": "invoice",
            "name": "invoice-item",
            "template": "admin_specification/include/ajax_invoice_item.html",
        },
        {
            "module": "vacancy",
            "name": "vacancy-item",
            "template": "vacancy_web/includes/ajax_vacancy_item.html",
        },
        {
            "module": "search",
            "name": "search-elem",
            "template": "product/includes/ajax_search_elem.html",
        },
    ]

    for template_item in template_list:
        loaded_template = loader.get_template(template_item["template"])
        template_item["template"] = loaded_template.template.source

    return {
        "template_list": template_list,
    }

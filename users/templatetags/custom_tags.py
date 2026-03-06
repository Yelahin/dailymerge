from django import template

register = template.Library()

@register.filter
def get_category(source_category_map, source_id):
    return source_category_map.get(source_id, 'Unknown').name
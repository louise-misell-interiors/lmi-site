from django import template

register = template.Library()


@register.filter('get_dict_key')
def get_dict_key(h, key):
    return h[key]

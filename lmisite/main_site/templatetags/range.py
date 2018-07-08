from django import template

register = template.Library()


@register.filter(name='range')
def range_filter(value):
    return range(value)


@register.filter(name='mod')
def mod_filter(value, mod):
    return value % mod

from django import template

register = template.Library()

@register.filter(name='lookup')
def lookup(dict, key):
    return dict[key]
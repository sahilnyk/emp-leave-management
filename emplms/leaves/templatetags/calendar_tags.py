from django import template
from datetime import date

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])

@register.simple_tag
def make_date(day, month, year):
    try:
        return date(int(year), int(month), int(day))
    except:
        return None
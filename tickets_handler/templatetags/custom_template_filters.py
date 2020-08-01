from django import template
import json
from django.conf import settings
register = template.Library()

@register.filter(name='phones_string_to_dict')
def phones_string_to_dict(value):
    data = value.replace("\'", "\"")
    try:
        data = json.loads(data)
    except:
        return None
    return data

# settings value
@register.simple_tag
def settings_value(name):
    return getattr(settings, name, "")
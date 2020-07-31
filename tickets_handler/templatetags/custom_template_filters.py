from django import template
import json
register = template.Library()

#TODO:not working in tempate return 'phone instead' dict obj
def phones_string_to_array(value):
    data = value.replace(']', '').replace('[', '').replace("\'", "\"")
    try:
        data = json.loads(data)
    except:
        return None
    return data

register.filter('phones_string_to_array', phones_string_to_array)
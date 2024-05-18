from django import template

register = template.Library()


@register.filter
def data_type(value):
    try:
        value = int(value)
    except:
        pass
    return type(value).__name__


@register.filter
def data_type_1(value):
    try:
        value = int(value)
    except:
        pass
    return value


@register.filter
def starts_with(value, arg):
    """Custom template filter to check if a string starts with a specific prefix."""
    return value.startswith(arg)

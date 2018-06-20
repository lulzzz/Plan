from django import template

register = template.Library()

@register.filter(name='verbose_name')
def verbose_name(value, arg):
    return value._meta.get_field(arg).verbose_name

@register.filter
def index(List, i):
    return List[int(i)]

@register.filter
def percentagecomma(value):
    return "{0:.2f}%".format(value)

@register.filter
def percentagemultiplied(value):
    return "{0:.2f}%".format(value*100)

@register.filter
def intcomma_rounding2(value):
    return "{0:,.2f}".format(value)

@register.filter
def intcomma_rounding0(value):
    return "{0:,.0f}".format(value)

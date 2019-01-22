from django import template

import math

register = template.Library()

#def cut(value, arg):
#    return value.replace(arg, '')

def as_html(obj):
    """A helper function for the admin panel"""
    if hasattr(obj, 'username'):
        return obj.username
    if hasattr(obj, 'as_html'):
        print("xxx")
        return obj.as_html()
    if hasattr(obj, 'name'):
        return obj.name
    return "I don' t know"

register.filter('as_html', as_html)

#add more than one and include old classes
@register.filter(name='addattr')
def addattr(field, css):
    """Adds the specified attributes to the html"""
    attrs = {}
    definition = css.split(',')
    if field.field.widget.attrs.get('class', None):
        classes = field.field.widget.attrs.get('class', None)
    else:
        classes = ''

    for d in definition:
        t, v = d.split(':')
        if t == 'class':
            classes += ' ' + v
        else:
            attrs[t] = v

    attrs['class'] = classes

    return field.as_widget(attrs=attrs)

#keep old classes too
#def addcss(field, css):
#class_old = field.field.widget.attrs.get('class', None)
#class_new = class_old + ' ' + css if class_old else css
#return field.as_widget(attrs={"class": class_new})

#def addcss(field, css):
   #return field.as_widget(attrs={"class":css})

@register.filter(name='as_service_level')
def as_service_level(field):
    """It changes the service_level (number) to text"""
    field = int(field)
    if field == 0:
        return 'None'
    elif field == 1:
        return 'Bronze'
    elif field == 2:
        return 'Silver'
    elif field == 3:
        return 'Gold'
    else:
        return 'Unknown'


@register.filter(name="date_format")
def date_format(datum):
    """Sets english date format"""
    if datum:
        return datum.strftime('%d/%m/%Y')
    return datum


@register.filter(name='ago')
def ago(second):
    try:
        second = int(second)
    except ValueError:
        return "<I>%s</I>" % second
    years = math.floor(second / (365 * 86400))
    remaining = second % (365 * 86400)
    days = math.floor(remaining / (86400))
    remaining = second % 86400
    hours = math.floor(remaining / 3600)
    remaining = second % 3600
    minutes = math.floor(remaining / 60)
    seconds = second % 60
    ret_str = ''
    if years:
        ret_str += '<font color="red">%s</font>y' % years
    if days:
        ret_str += ' <font color="blue">%s</font>d' % days
    if hours:
        ret_str += ' <font color="green">%s</font>h' % hours
#    if minutes:
#        ret_str += ' <font color="green">%s</font>m' % minutes
#    if seconds:
#        ret_str += ' <font color="r">%s</font>s' % seconds
    return ret_str


@register.filter(name='template_exists')
def template_exists(template_name):
    try:
        template.loader.get_template(template_name)
        return True
    except template.TemplateDoesNotExist:
        return False

@register.filter(name='ifinlist')
def ifinlist(value, lst):
    """Checks if string is in a comma separated list"""
    return value in lst.split(',')
    
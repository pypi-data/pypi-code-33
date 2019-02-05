from django import template, forms

register = template.Library()


@register.simple_tag(takes_context=True)
def pagination_pagelink(context, value):
    request = context["request"]
    r = request.GET.copy()
    r["page"] = str(value)
    urlencode = r.urlencode()
    return urlencode


@register.filter()
def form_styling(field):
    def styling(field, klass):
        field.field.widget.attrs.update({"class": klass})
        return field

    widget = field.field.widget
    input_type = (forms.TextInput, forms.PasswordInput, forms.EmailInput, forms.NumberInput)
    textarea_type = (forms.Textarea,)
    if isinstance(widget, input_type):
        return styling(field, "input")
    elif isinstance(widget, textarea_type):
        return styling(field, "textarea")

    return field

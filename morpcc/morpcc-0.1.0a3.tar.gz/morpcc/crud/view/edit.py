import morepath
import html
import deform
from morpfw.crud import permission as crudperms
from ..model import CollectionUI, ModelUI
from ...app import App
from ...util import dataclass_to_colander


@App.html(model=ModelUI, name='edit', template='master/crud/form.pt',
          permission=crudperms.Edit)
def edit(context, request):
    formschema = dataclass_to_colander(
        context.model.schema, include_fields=context.edit_include_fields,
        exclude_fields=context.edit_exclude_fields)
    data = context.model.data.as_dict()
    return {
        'page_title': 'Edit %s' % html.escape(str(context.model.__class__.__name__)),
        'form_title': 'Edit',
        'form': deform.Form(formschema(), buttons=('Submit',)),
        'form_data': data,
    }


@App.html(model=ModelUI, name='edit', template='master/crud/form.pt',
          permission=crudperms.Edit, request_method='POST')
def process_edit(context, request):
    formschema = dataclass_to_colander(
        context.model.schema, include_fields=context.edit_include_fields,
        exclude_fields=context.edit_exclude_fields)
    data = context.model.data.as_dict()

    controls = list(request.POST.items())
    form = deform.Form(formschema(), buttons=('Submit', ))

    failed = False
    try:
        data = form.validate(controls)
    except deform.ValidationFailure as e:
        form = e
        failed = True

    if not failed:
        context.model.update(data)
        return morepath.redirect(request.link(context))

    return {
        'page_title': 'Edit %s' % html.escape(str(context.model.__class__.__name__)),
        'form_title': 'Edit',
        'form': form,
        'form_data': data,
    }

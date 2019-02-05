from django.http import HttpResponse
from django.http import Http404

from django_data_tables import POOL

def get_table_or_404(table_name):
    table = POOL.get(table_name)
    if table is None:
        raise Http404('Table Identifier not found: "{}"'.format(table_name))
    return table

def get_data(request, table_name):
    table = get_table_or_404(table_name)
    return table.get_data(request)

def action(request, table_name):
    table = get_table_or_404(table_name)
    action_id = request.GET.get(
        'action_id',
        request.POST.get('action_id', None)
    )
    try:
        action = table.get_action(action_id)
    except ValueError:
        return HttpResponse(
            'cannot find any action with id "{}"'
            .format(action_id),
            status=400
        )
    objects = table.get_objects(request)
    if not objects:
        return HttpResponse(
            'cannot find any items to work with',
            status=400
        )
    obj = None
    if action.is_single and objects.count() == 1:
        obj = objects[0]
    if not action.is_available(request, obj):
        return HttpResponse('this is not allowed', status=403)
    if request.method == "GET":
        return action.get(request, objects)
    elif request.method == "POST":
        response = action.post(request, objects)
        if response is None:
            return HttpResponse('')
        if isinstance(response, str):
            return HttpResponse(response)
        return response
    return HttpResponse('table actions only support GET and POST', status=400)



from django.apps import apps
from django.http import JsonResponse, HttpResponseRedirect
import json

def redirect(request,url=None):
    return HttpResponseRedirect(url)

def list_view(request,app_name,model_name):
    app = apps.get_app_config(app_name)
    model = app.get_model(model_name)
    data = json.loads(request.body.decode('utf-8') or "{}")
    if data:
        id = data.pop("id",None)
        if id:
            obj = model.from_data(data,request=request,id=id)
        else:
            obj = model.from_data(data,request=request)
        obj.save()
        return JsonResponse(obj.as_json)
    items = model.objects.request_filter(request)
    return JsonResponse({
        'results': [i.as_json for i in items],
    })

def user_json(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({})
    keys = ['id','username','email','is_superuser','is_staff']
    return JsonResponse({
        'user': { k: getattr(user,k) for k in keys },
    })
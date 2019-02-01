
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
import json
from django.views.decorators.csrf import csrf_exempt
from .models import *

# Create your views here.
def index(request):
    return render(request, 'django_assistant/index.html', {})

def decode_dict(dict1):
    keys = dict1.keys()
    for key in keys:
        if type(dict1[key]) == dict:
            decode_dict(dict1[key])
    return ""

@csrf_exempt
def a_create_api(request):
    #~ import ipdb;ipdb.set_trace()
    edit_mode = request.POST.get("edit_mode",None)
    api_id = request.POST.get("api_id",None)
    url = request.POST.get("url",None)
    params = request.POST.get("params",None)
    desc = request.POST.get("descr",'')
    http_type = request.POST.get("http_type",None)

    if edit_mode == "add":
        api = Api()

    if edit_mode == "edit":
        api = Api.objects.get(id=api_id)

    api.url = url
    api.desc = desc
    api.http_type = http_type
    api.save()

    dict1 = {}
    dict1["result"] = "Success"
    return HttpResponse(json.dumps(dict1),content_type="application/json")

@csrf_exempt
def a_edit_params(request):
    edit_mode = request.POST.get("edit_mode",None)
    params = eval(request.POST.get("params",None))
    api_id = request.POST.get("api_id",None)
    apiparam_id = request.POST.get("apiparam_id",None)
    #~ tags = eval(request.POST.get("tags",None))

    if edit_mode == "add":
    	api = Api.objects.get(id=api_id)
    	param = ApiParam()
    	param.params = params
    	param.save()
    	api.params.add(param)

    if edit_mode == "edit":
    	param = ApiParam.objects.get(id=apiparam_id)
    	param.params = params
    	param.save()

    #~ for tag in param.tags.all():
	#~ param.tags.remove(tag)

    #~ for tag in tags:
	#~ tag = Tag.objects.get(id=tag)
	#~ param.tags.add(tag)



    dict1 = {}
    dict1["result"] = "Success"
    return HttpResponse(json.dumps(dict1),content_type="application/json")

@csrf_exempt
def a_get_apis(request):

    list1 = []

    for api in Api.objects.all():
        list2 = []
        dict2 = {}
        dict2["api_id"] = api.id
        dict2["url"] = api.url
        dict2["params"] = api.get_params()
        dict2["http_type"] = api.http_type
        dict2["api_status"] = api.status
        list1.append(dict2)

    dict1={}
    dict1["result"] = "Success"
    dict1["response"] = list1
    return HttpResponse(json.dumps(dict1),content_type="application/json")

@csrf_exempt
def a_fetch_api_details(request):
    api_id = request.POST.get("api_id",None)

    api = Api.objects.get(id=api_id)
    api_dict = {}
    api_dict["id"] = api.id
    api_dict["url"] = api.url
    api_dict["params"] = api.get_params()
    api_dict["http_type"] = api.http_type
    api_dict["api_status"] = api.status
    api_dict["descr"] = api.desc

    dict1 = {}
    dict1["api"] = api_dict
    dict1["result"] = "Success"
    return HttpResponse(json.dumps(dict1),content_type="aplication/json")


@csrf_exempt
def a_delete_api(request):
    api_id = request.POST.get("api_id",None)
    api = Api.objects.get(id=api_id)
    for param in api.params.all():
        param.delete()

    api.delete()

    dict1 = {}
    dict1["result"] = "Success"
    return HttpResponse(json.dumps(dict1),content_type="application/json")


@csrf_exempt
def a_trial_api(request):

    dict1 = {}
    dict1["sample"] = [{"name":"jerin","age":"25"},{"name":"jerin2","age":"26"}]
    return HttpResponse(json.dumps(dict1),content_type="aplication/json")


@csrf_exempt
def a_edit_api_status(request):
    api_id = request.POST.get("api_id",None)
    api_status = request.POST.get("api_status",None)

    api = Api.objects.get(id=api_id)
    api.status = api_status
    api.save()
    dict1 = {}
    dict1["result"] = "Success"
    return HttpResponse(json.dumps(dict1),content_type="application/json")

@csrf_exempt
def a_edit_api(request):
    edit_element = request.POST.get("edit_element",None)
    api_id = request.POST.get("api_id",None)
    api = Api.objects.get(id=api_id)

    if edit_element == "basic_info":
        url = request.POST.get("url",None)
        http_type = request.POST.get("http_type",None)
        api.url = url
        api.http_type = http_type
        api.save()

    if edit_element == "info":
        description = request.POST.get("description",None)
        api.desc = description
        api.save()


    dict1 = {}
    dict1["result"] = "Success"
    return HttpResponse(json.dumps(dict1),content_type="application/json")

@csrf_exempt
def a_delete_api_input(request):
    input_id = request.POST.get("input_id",None)
    inputset = ApiParam.objects.get(id=input_id)
    inputset.delete()

    dict1 = {}
    dict1["result"] = "Success"
    return HttpResponse(json.dumps(dict1),content_type="application/json")


@csrf_exempt
def a_get_tags(request):
    list1 = []
    for tag in Tag.objects.all():
    	dict2={}
    	dict2["name"] = tag.name
    	dict2["id"] = tag.id
    	list1.append(dict2)

    dict1 = {}
    dict1["result"] = "Success"
    dict1["tags"] = list1
    return HttpResponse(json.dumps(dict1),content_type="application/json")

import os
from django.conf import settings

@csrf_exempt
def codebase_index(request):
    return render(request, 'django_assistant/codebase_index.html', {})


import string
def show_urls(urllist, depth=0):
    list2 = []
    for entry in urllist:
    	#~ print "  " * depth, entry.regex.pattern
    	if hasattr(entry, 'url_patterns'):
    		show_urls(entry.url_patterns, depth + 1)
    	else:
    	    url_temp = string.replace(entry.regex.pattern,'^','/')
    	    url_temp = string.replace(url_temp,'$','')
    	    list2.append(url_temp)
    return list2


from django.urls import reverse
import urllib
def code_base_info(request):
    views_dict = {}
    models_dict = {}
    tasks_dict = {}
    urls_dict = {}
    ajaxcalls_dict = {}
    csvdetails_dict = {}
    views_html_mapper_dict = {}
    apps = ['buzz','commons','core','profiles','networks','library','fabadmin','messagingapps', 'educator', 'tests2']
    for app in apps:
    	#views
    	list1 = []
    	list2 = []
    	views_file = os.path.join(settings.BASE_DIR,app,'views.py')

    	for line in file(views_file):
    	    if line.startswith('def'):
                view_name = line[4:line.index('(')]
    	    if line.strip().startswith('return render_to_response'):
        		end = line.strip().index('(')
        		begin = line.strip().index(',')
        		html_name = line.strip()[end+2:begin-1].split('/')[-1]
        		view_html_mapper_dict = {'views':view_name,'html':html_name}
        		list2.append(view_html_mapper_dict)
    		#~ try:
    		    #~ current_url =  reverse(app+".views."+view_name)
    		    #~ if urllib.urlopen("http://www.fabgrad.com/"+current_url).getcode() != 200:
    			#~ print current_url , view_name , html_name
    		#~ except:
    		    #~ print "no url for ",view_name
    	views_html_mapper_dict[app] = list2


    	for line in file(views_file):
    	    if line.startswith('def'):
                list1.append(line[4:line.index('(')])
    		#~ print line[4:line.index('(')]
    	views_dict[app] = list1


	#models
    list1 = []
    models_name = app + ".models"

    try:
        models_module = __import__(models_name, fromlist=["models"])
        attributes = dir(models_module)
        for attr in attributes:
            try:
                attrib = models_module.__getattribute__(attr)
                if issubclass(attrib, models.Model) and attrib.__module__== models_name:
                    list1.append(attr)
            except:
                pass
    except:
        pass

    models_dict[app] = list1

    #tasks
    list1 = []
    tasks_file = os.path.join(settings.BASE_DIR,app,'tasks.py')
    try:
        for line in file(tasks_file):
        	if line.startswith('def'):
        	    list1.append(line[4:line.index('(')])
        	    #~ print line[4:line.index('(')]
    except:
        pass
    tasks_dict[app] = list1

    #ajax calls
    #~ js_files = os.path.join(settings.BASE_DIR,'static_media/new/js')
    #~ for jsFile in os.listdir(js_files):
    #~ list1 = []
    #~ enter=0
    #~ enter2=0
    #~ try:
        #~ file_path = os.path.join(js_files,jsFile)
        #~ for line in file(file_path):
    	#~ if enter and 'AJAX calls' not in line and len(line.strip()):
    	    #~ list1.append(line.split('\n')[0])
    	#~ if 'AJAX calls' in line:
    	    #~ if enter:
    		#~ enter = 0
    	    #~ else:
    		#~ enter=1
    	#~ if "$.ajax({" in line:
    	    #~ enter2 = 1
    	#~ if enter2:
    	    #~ "url" in line
    	    #~ if "url" in line:
    		#~ print jsFile, line.strip().split(':')[1].split(',')[0]
    		#~ enter2 = 0
    	#~
    #~ except:
        #~ pass
    #~
    	#~
    #~ ajaxcalls_dict[jsFile] = list1

    #~ ===========================

    #~ temp_dict = {}
    template_path = os.path.join(settings.BASE_DIR,'templates')
    for subdir, dirs, files in os.walk(template_path):
        for file1 in files:
            enter2 = 0
            enter3 = 0
            list1 = []
            #print os.path.join(subdir, file)
            file_path = subdir + os.sep + file1
            for line in file(file_path):
            	if "$.ajax({" in line:
            	    #~ print "AJAX",line.strip()
            	    enter2 = 1
            	elif "$.getJSON(" in line:
            	    enter3 = 1
            	if enter2:
            	    "url" in line
            	    if "url" in line:
                		list1.append({'file_name':file1,'url':line.strip().split(':')[1].split(',')[0]})
                		#~ print file1, line.strip().split(':')[1].split(',')[0]
                		enter2 = 0
            	if enter3:
            	    #~ print "getJSON : ",line.split('(')[1].split(',')[0]
            	    list1.append({'file_name':file1,'url':line.split('(')[1].split(',')[0]})
            	    enter3 = 0
            	ajaxcalls_dict[file1] = list1

    #csv searcher
    #~ list1 = []
    #~ var_in = False
    #~ csv_path = os.path.join(settings.BASE_DIR,'static_media/new/style/')
    #~ for subdir, dirs, files in os.walk(csv_path):
    #~ for file1 in files:
        #~ file_path = subdir + os.sep + file1
        #~ for line in file(file_path):
    	#~ if line.startswith('.') or line.startswith('#'):
    	    #~ var_in = True
    	    #~ list1.append({'file_name':file1,'line':unicode(line, errors='replace')})
    	    #~ print line
        #~ csvdetails_dict[file1] = list1

    #urls
    import fabgrad.urls
    urllist = fabgrad.urls.urlpatterns
    urls_dict = show_urls(urllist)
    #~ urls_dict = {}

    dict1 = {}
    dict1['views_html_mapper'] = views_html_mapper_dict
    dict1['views'] = views_dict
    dict1['models'] = models_dict
    dict1['tasks'] = tasks_dict
    dict1['ajaxcalls'] = ajaxcalls_dict
    dict1['csvdetails'] = csvdetails_dict
    dict1['urls'] = urls_dict
    dict1['result'] = "Success"

    return HttpResponse(json.dumps(dict1),content_type="application/json")


@csrf_exempt
#~ @staff_member_required
#~ def model_details(app_name,model_name):
def model_details(request):
    enter = 0
    fields=[]
    code=[]
    model_name = request.POST.get('model_name',None)
    app_name = request.POST.get('app_name',None)
    entity = app_name+"_"+model_name
    x = __import__(app_name+'.models')
    fields = eval('x.models.'+model_name+'._meta.get_all_field_names()')
    for line in file(os.path.join(settings.BASE_DIR,app_name,'models.py')):

    	if line.startswith('class') or enter:
    	    try:
        		if line[6:line.index('(')] == model_name:

        		    enter = 1
        		    code.append(line)
        		if line.split('=')[0].strip() in fields:
        		    code.append(line)
        		    enter = 2
        		elif enter==2:
        		    enter=0
    	    except:
                pass

    dict1={}
    dict1['result'] = "Success"
    dict1['code'] = code
    return HttpResponse(json.dumps(dict1),content_type="application/json")


@csrf_exempt
def a_create_model_relationship_diagram(request):
    model_names = eval(request.POST.get('model_names',None))

    directory = settings.MEDIA_ROOT+'/django_assistant/'
    try:
        if os.path.exists(directory):
            os.remove(directory+'models_relationship_graph.png')
    except:
        pass
    from django.core.management import call_command
    if not os.path.exists(directory):
        os.makedirs(directory)
        #~ import ipdb;ipdb.set_trace()
        call_command('graph_models','-a','-I '+model_names,'-o'+directory+'models_relationship_graph.png')

    #~ graph_models -a -I Foo,Bar -o models_relationship_graph.png
    dict1 = {}
    dict1['relationship_diagram'] = settings.MEDIA_URL+'django_assistant/models_relationship_graph.png'
    dict1['result'] = "Success"
    return HttpResponse(json.dumps(dict1),content_type="application/json")

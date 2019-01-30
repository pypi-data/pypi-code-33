
from tableau_tools.tableau_rest_api import *
from tableau_tools import *

username = 'bhowell'
password = 'aq12wsDe#'
server = 'http://scvwtechcomp.tsi.lan'
site_content_url = 'agency'

t = TableauRestApiConnection32(server=server, username=username, password=password, site_content_url=site_content_url)
t.signin()


def index(request):
    return HttpResponse("REST calls only")


def groups(request):
    g_sort = Sort('name', 'asc')
    g = t.query_groups_json(sorts=[g_sort, ])
    return JsonResponse(g)


def users(request):
    user_sort = Sort('name', 'asc')
    u = t.query_users_json(all_fields=False, fields=['id', 'name'], sorts=[user_sort, ])
    return JsonResponse(u)


def projects(request):
    # May want to strip out owner information and contentPermissions. No "fields" option for projects call
    p_sort = Sort('name', 'asc')
    p = t.query_projects_json(sorts=[p_sort, ])
    return JsonResponse(p)


def workbooks(request, username=None):
    w = t.query_workbooks_json()
    return JsonResponse(w)


def datasources(request, username=None):
    d = t.query_datasources_json(all_fields=False, fields=['id', 'name', 'contentUrl', 'project.id', 'project.name'])
    return JsonResponse(d)


def views(request, username=None):
    v = t.query_views_json()
    return JsonResponse(v)


def views_in_workbook(request, workbook_luid):
    v = t.query_workbook_views_json(wb_name_or_luid=workbook_luid)
    return JsonResponse(v)
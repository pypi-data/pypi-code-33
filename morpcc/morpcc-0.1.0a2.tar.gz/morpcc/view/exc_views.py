import morpfw
import morepath
from morepath.authentication import NO_IDENTITY
from webob.exc import HTTPNotFound, HTTPForbidden, HTTPInternalServerError
import urllib.parse
from ..app import App
from ..root import Root


@App.html(model=HTTPNotFound, template='master/error_404.pt')
def httpnotfound_error(context, request):
    @request.after
    def adjust_status(response):
        response.status = 404
    return {'status': 'error',
            'message': 'Object Not Found : %s' % request.path}


@App.html(model=HTTPForbidden, template="master/error_403.pt")
def forbidden_error(context, request):
    if request.identity is NO_IDENTITY:
        return morepath.redirect('/login?came_from=%s' % urllib.parse.quote(request.url))

    @request.after
    def adjust_status(response):
        response.status = 403
#   FIXME: should log this when a config for DEBUG_SECURITY is enabled
#    logger.error(traceback.format_exc())
    return {'status': 'error',
            'message': 'Access Denied : %s' % request.path}

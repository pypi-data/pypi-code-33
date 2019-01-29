import json

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.generic.edit import DeletionMixin

from .decorators import ajax_required, login_required_ajax


class AjaxRequiredMixin(object):

    @method_decorator(ajax_required)
    def dispatch(self, *args, **kwargs):
        return super(AjaxRequiredMixin, self).dispatch(*args, **kwargs)


class AjaxMixin(AjaxRequiredMixin):
    """
    A mixin that raise 400 if request was not POST or was made not using ajax.
    Also render response as json.
    """
    response_class = HttpResponse

    def render_to_response(self, context=None, **response_kwargs):
        """
        Return a JSON response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(self.convert_context_to_json(context or {}), **response_kwargs)

    def convert_context_to_json(self, context):
        """
        Convert the context dictionary into a JSON object
        """
        return json.dumps(context, cls=DjangoJSONEncoder)


class LoginRequiredMixin(object):

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(*args, **kwargs)


class StaffRequiredMixin(object):

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(StaffRequiredMixin, self).dispatch(*args, **kwargs)


class LoginRequiredAjaxMixin(object):

    @method_decorator(login_required_ajax)
    def dispatch(self, *args, **kwargs):
        return super(LoginRequiredAjaxMixin, self).dispatch(*args, **kwargs)


class AjaxableResponseMixin(object):

    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {'pk': self.object.pk, }
            return self.render_to_json_response(data)
        else:
            return response


class AjaxDeletionMixin(AjaxableResponseMixin, DeletionMixin):
    """
    A mixin providing the ability to delete objects with ajax response
    """

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return self.render_to_json_response({
            'status': 'success',
            'redirect_to': success_url
        })


class OnlyOwnerObjectRequiredMixin(object):

    def get_object(self, queryset=None):
        obj = super(OnlyOwnerObjectRequiredMixin, self).get_object(queryset)
        if obj.user != self.request.user:
            raise PermissionDenied
        return obj

    def get_queryset(self):
        qs = super(OnlyOwnerObjectRequiredMixin, self).get_queryset()
        return qs.filter(user=self.request.user)

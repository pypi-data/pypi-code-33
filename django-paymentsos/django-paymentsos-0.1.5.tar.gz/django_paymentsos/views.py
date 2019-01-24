import copy
import json

from django.http.response import HttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from django_paymentsos.forms import PaymentNotificationForm


@method_decorator(csrf_exempt, name='dispatch')
class PaymentNotificationView(View):
    form_class = PaymentNotificationForm

    def post(self, request):
        x_zooz_request_id = request.META.get('HTTP_X_ZOOZ_REQUEST_ID')
        x_payments_os_env = request.META.get('HTTP_X_PAYMENTS_OS_ENV')
        version = request.META.get('HTTP_VERSION')
        event_type = request.META.get('HTTP_EVENT_TYPE')
        signature = request.META.get('HTTP_SIGNATURE')

        body = json.loads(request.body)

        body['raw'] = copy.copy(body)
        body['webhook_id'] = body.pop('id')
        body['created'] = timezone.datetime.strptime(body.get('created'), '%Y-%m-%dT%H:%M:%S.%fZ')
        body['x_zooz_request_id'] = x_zooz_request_id
        body['x_payments_os_env'] = x_payments_os_env
        body['version'] = version
        body['event_type'] = event_type
        body['signature'] = signature

        data = body.pop('data')
        data['data_id'] = data.pop('id')
        data['notification_created'] = data.pop('created')

        if 'provider_specific_data' in data:
            provider_specific_data = data.pop('provider_specific_data')
            data.update(provider_specific_data)

        if 'payment_method' in data:
            payment_method = data.pop('payment_method')
            payment_method['method_created'] = payment_method.pop('created')
            data.update(payment_method)

        if 'result' in data:
            result = data.pop('result')
            result['result_status'] = result.pop('status')
            result['result_description'] = result.pop('description', '')
            data.update(result)

        if 'provider_data' in data:
            provider_data = data.pop('provider_data')
            provider_data['provider_description'] = provider_data.pop('description')
            provider_data['raw_response'] = json.loads(provider_data.get('raw_response'))
            data.update(provider_data)

        body.update(data)

        form = self.form_class(body)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        return HttpResponse(form.errors, status=400)

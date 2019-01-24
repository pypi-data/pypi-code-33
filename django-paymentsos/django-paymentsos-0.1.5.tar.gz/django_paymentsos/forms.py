from django import forms

from django_paymentsos.models import PaymentsOSNotification


class PaymentNotificationForm(forms.ModelForm):
    class Meta:
        model = PaymentsOSNotification
        fields = '__all__'

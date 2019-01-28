from django.forms.fields import CharField
from stem_feedback.models import *
from django import forms
from django.utils.translation import ugettext as _


class FeedbackEmailForm(forms.ModelForm):
    from_email = forms.EmailField(required=True, label=_('Ваш email'))
    subject = CharField(max_length=30, required=False, label=_("Тема обращения"))
    type = forms.ModelChoiceField(queryset=FeedBackType.objects.filter(feedback_type='event'),
                                            required=False,
                                            label=_('Тип обращения'))
    message = forms.CharField(widget=forms.Textarea, required=True, label=_('Текст'))

    def __init__(self, *args, **kwargs):
         from django.forms.widgets import HiddenInput
         super().__init__(*args, **kwargs)
         initial = kwargs.get('initial', False)
         if initial['user']!=None:
             self.fields['from_email'].widget = HiddenInput()
             self.fields['from_email'].required = False
    class Meta:
        model = Feedback
        fields = (
            'from_email',
            'subject',
            'type',
            'message',
        )


SETTLEMENT_ACCOUNT = 'settlement_account'
CARD_ACCOUNT = 'card_account'
COURIER = 'courier'
PAYMENT_CHOICES = (
    (SETTLEMENT_ACCOUNT, 'Расчетный счет'),
    (CARD_ACCOUNT, 'Карточный счет'),
    (COURIER, 'Курьер'),
)


class PaymentNotificationForm(forms.Form):
    payment_type = forms.ChoiceField(choices=PAYMENT_CHOICES,
                                     widget=forms.RadioSelect(), label=_("Форма оплаты"))
    sum = forms.DecimalField(max_digits=15, decimal_places=3, initial=1, label=_("Сумма"))

    currency = forms.ChoiceField(required=False,
                                 choices=[],
                                 widget=forms.Select,
                                 label=_('Валюта'))

    customer = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select,
        label=_('Покупатель'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial = kwargs.get('initial', False)
        if initial:
            self.fields['customer'].choices = initial.get('customers', [])
            self.fields['currency'].choices = initial.get('currency', [])


DEFECT = 'Брак'
DAMAGED = 'Не соответствует артикулу/поврежден'
RETAINED = 'Не забрал клиент'
REFUSAL = 'Отказ клиента'
ERROR_CLIENT = 'Ошибка клиента'
ERROR_OF_SELECTION = 'Ошибка при подборе'

MONEYBACK_CHOICES = (
    (DEFECT, 'Брак'),
    (DAMAGED, 'Не соответствует артикулу/поврежден'),
    (RETAINED, 'Не забрал клиент'),
    (REFUSAL, 'Отказ клиента'),
    (ERROR_CLIENT, 'Ошибка клиента'),
    (ERROR_OF_SELECTION, 'Ошибка при подборе'),
)


class MoneyBackForm(forms.Form):

    comment = forms.CharField(widget=forms.Textarea, required=False, label=_("Комментарий"))
    tracking_number = forms.CharField(max_length=255, required=False, label=_("Номер декларации"))

    reason_for_the_return = forms.ChoiceField(
        required=False,
        choices=MONEYBACK_CHOICES,
        widget=forms.Select,
        label=_('Причина возврата'))

    ship = forms.ChoiceField(
        required=False,
        choices=[],
        widget=forms.Select,
        label=_('Доставка'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial = kwargs.get('initial', False)
        if initial:
            self.fields['ship'].choices = initial.get('ships', [])


class OrdersForm(forms.Form):
    name = forms.CharField(max_length=255, required=False, label=_("Наименование"))
    quantity = forms.DecimalField(max_digits=15, decimal_places=3, initial=1, label='Количество товара в накладной')
    return_qty = forms.DecimalField(max_digits=15, decimal_places=3, required=True, label='Возврат')


class CallBackForm(forms.Form):
    phone_number = forms.CharField(max_length=255, required=True, label="Номер телефона")
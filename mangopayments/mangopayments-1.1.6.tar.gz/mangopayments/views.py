from django.template.response import TemplateResponse
from mangopayments.models import MangoPayCardRegistration, MangoPayUser

from django.conf import settings


def mangopay_test(request):
    card_registration = MangoPayCardRegistration()
    card_registration.mangopay_user = MangoPayUser.objects.get(id=2)
    card_registration.save()
    card_registration.create("EUR", "MAESTRO")

    card_data = card_registration.get_preregistration_data()
    accessKey = card_data['accessKey']
    cardRegistrationURL = card_data['cardRegistrationURL']
    preregistrationData = card_data['preregistrationData']
    id = card_registration.mangopay_id

    context = {"access_key": accessKey,
               "card_registration_URL": cardRegistrationURL,
               "preregistration_data": preregistrationData,
               "card_registration_id": id,
               "clientId": settings.MANGOPAY_CLIENT_ID,
               "baseURL": settings.MANGOPAY_BASE_URL}

    return TemplateResponse(request, "mangopay_test.html", context)

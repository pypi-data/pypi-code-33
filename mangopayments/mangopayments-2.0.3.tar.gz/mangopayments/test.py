import django

django.setup()

from mangopayments.models import MangoPayBankAccount

acc = MangoPayBankAccount.objects.get(id=2)

acc.update()
def check_user_subscription(func):
    """
    This redirect to the choose-plan template, in case that used doesn't have a active subcription.
    #TODO how determined if the package is active ?
    """

    def wrapper(request, *args, **kwargs):
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        from ccc.packages.models import PurchasedPackage

        package = PurchasedPackage.objects.filter(user=request.user.id)

        if not package:
            return HttpResponseRedirect(reverse('srm:packages:select_plan'))

        return func(request, *args, **kwargs)

    return wrapper

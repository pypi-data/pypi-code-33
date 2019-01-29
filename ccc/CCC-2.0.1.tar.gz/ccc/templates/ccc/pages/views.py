from apps.packages.models import PackageType
from apps.pages.forms import ContactUsForm
from django.conf import settings
from django.contrib import messages
from django.core.mail.message import EmailMessage
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView
from django.views.generic.edit import FormView


def home(request):
    plans = PackageType.subscription_objects.all()

    if request.user.is_authenticated():
        return HttpResponseRedirect('/user/dashboard/')
    else:
        return render(request, 'ccc/pages/home.html', locals())


def payment(request):
    return render(request, 'ccc/pages/payment.html')


class PricingView(TemplateView):
    """
    Pricing page View
    """
    template_name = 'ccc/pages/pricing.html'

    def get_context_data(self, **kwargs):
        plans = PackageType.subscription_objects.all()
        if 'view' not in kwargs:
            kwargs['view'] = self
        kwargs['plans'] = plans
        return kwargs


class ContactUsView(FormView):
    """Class view for handling contact us form
    """
    success_url = reverse_lazy("home")
    form_class = ContactUsForm
    template_name = "ccc/pages/home.html"

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        request = self.request
        contact_email = request.POST.get(
            'contact_email', '')
        form_content = request.POST.get('content', '')

        # Email the profile with the
        # contact information
        #         template = get_template('contact_template.txt')
        #         context = Context({
        #             'contact_email': contact_email,
        #             'form_content': form_content,
        #         })
        #         content = template.render(context)
        content = form_content
        email = EmailMessage(
            "New contact form submission",
            content,
            "Your website" + '',
            [settings.CONTACT_US_EMAIL],
            headers={'Reply-To': contact_email}
        )
        email.send()
        messages.info(
            request,
            'Your query has been successfully send. We will get back to you\
             within 24 hours'
        )
        return HttpResponseRedirect(self.get_success_url())

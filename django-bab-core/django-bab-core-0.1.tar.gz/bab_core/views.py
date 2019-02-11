from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail, BadHeaderError

from bab_cms.models import Post, Article, Category
from bab_project.models import Category as PrjCategory
from bab_project.models import Customer

from .forms import ProfileForm, UserForm, ContactForm

def index(request):
    project_categories = PrjCategory.objects.all()
    latest_posts = Post.published.all()[:5]
    latest_articles = Article.published.all()[:5]
    active_partners = [partner for partner in Customer.objects.all() if partner.projects.count() ]

    return render(request, template_name='site/index.html', context={
        'project_categories': project_categories,
        'latest_posts': latest_posts,
        'latest_articles': latest_articles,
        'active_partners': active_partners,
    })

def contact(request):
    if request.method == 'GET':
        contact_form = ContactForm()
        return render(request, template_name='bab_core/contact.html', context={
            'contact_form': contact_form
        })
    else:
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            subject = contact_form.cleaned_data['subject']
            from_email = contact_form.cleaned_data['from_email']
            message = contact_form.cleaned_data['message']
            try:
                send_mail("[%s] %s" % (from_email, subject), message, from_email, ['info@boite-a-bidules.com'])
            except Exception as e:
                messages.error(request, str(e))
                return render(request, template_name='bab_core/contact.html', context={
                    'contact_form': contact_form
                })

            messages.success(request, 'Votre message a bien été envoyé.')
            return redirect('core-index')


@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            return redirect('accounts-profile')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'profile/index.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

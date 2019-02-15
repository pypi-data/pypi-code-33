from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.db import transaction
from django.http.response import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import path, reverse
from django.views.decorators.http import require_http_methods

from django_support_lite.enums import Priority, ResponseType, Status
from django_support_lite.helpers import email
from django_support_lite.helpers.pagination import InvalidPageError, Pagination
from django_support_lite.helpers.upload import upload
from django_support_lite.models.image import Image
from django_support_lite.models.message import Message
from django_support_lite.models.ticket import Ticket
from django_support_lite.views.forms.message_create_form import MessageCreateForm
from django_support_lite.views.forms.ticket_create_form import TicketCreateForm


@login_required
@permission_required('django_support_lite.can_access')
@require_http_methods(['GET', 'POST'])
def view(request, ticket_id):
    try:
        ticket = Ticket.objects.select_related('user').get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return HttpResponseRedirect(
            reverse('django_support_lite:tickets.list')
        )

    if not request.user.has_perm('django_support_lite.can_manage'):
        if ticket.user.id != request.user.id:
            return HttpResponseRedirect(
                settings.LOGIN_URL
            )

    if request.method == 'POST':
        form = MessageCreateForm(request.POST, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                message = Message.objects.create(
                    ticket=ticket,
                    user=request.user,
                    text=form.cleaned_data['text']
                )

                # TODO: delete image on model delete
                for file in form.cleaned_data['images']:
                    Image.objects.create(
                        message=message,
                        path=upload(file)
                    )

                if request.user.has_perm('django_support_lite.can_manage'):
                    ticket.response_type = ResponseType.SUPPORT_RESPONSE
                else:
                    ticket.response_type = ResponseType.USER_RESPONSE

                ticket.save()

            def send_message_created(to):
                nonlocal request, ticket, message
                email.send(
                    request,
                    to,
                    'Response in ticket',
                    'message_created',
                    {
                        'url': request.build_absolute_uri(
                            reverse(
                                'django_support_lite:tickets.view',
                                kwargs={'ticket_id': ticket.id}
                            )
                        ) + '#message-{}'.format(message.id)
                    }
                )

            if request.user.has_perm('django_support_lite.can_manage'):
                if ticket.user.email:
                    send_message_created(ticket.user.email)
            else:
                if hasattr(settings, 'DSL_EMAIL_MANAGER'):
                    send_message_created(settings.DSL_EMAIL_MANAGER)

            messages.success(request, 'Message created.')

            return HttpResponseRedirect(
                reverse('django_support_lite:tickets.view', kwargs={'ticket_id': ticket_id})
            )

        messages.error(request, 'Error creating ticket message.')
    else:
        form = MessageCreateForm(initial=ticket.__dict__)

    return HttpResponse(
        render_to_string(
            'views/tickets/view.html',
            {
                'title': 'View Ticket',
                'ticket': ticket,
                'ticket_messages': ticket.message_set.select_related('user').order_by('-created_at').all(),
                'form': form,
                'Priority': Priority,
                'ResponseType': ResponseType,
                'Status': Status,
                'DSL_LAYOUT_NAME': settings.DSL_LAYOUT_NAME,
                'DSL_UPLOAD_URL_PREFIX': settings.DSL_UPLOAD_URL_PREFIX,
            },
            request
        )
    )

@login_required
@permission_required('django_support_lite.can_access')
@require_http_methods(['GET', 'POST'])
def create(request):
    if request.user.has_perm('django_support_lite.can_manage'):
        return HttpResponseRedirect(
            reverse('django_support_lite:tickets.list')
        )

    if request.method == 'POST':
        form = TicketCreateForm(request.POST, request.FILES)

        if form.is_valid():
            with transaction.atomic():
                ticket = Ticket.objects.create(
                    user=request.user,
                    title=form.cleaned_data['title'],
                    response_type=ResponseType.USER_RESPONSE,
                    status=Status.OPEN,
                    priority=Priority.NORMAL
                )

                message = Message.objects.create(
                    ticket=ticket,
                    user=request.user,
                    text=form.cleaned_data['text']
                )

                # TODO: delete image on model delete
                for file in form.cleaned_data['images']:
                    Image.objects.create(
                        message=message,
                        path=upload(file)
                    )

            if request.user.email:
                email.send(
                    request,
                    request.user.email,
                    'You\'ve created ticket',
                    'ticket_created_accessor',
                    {
                        'url': request.build_absolute_uri(
                            reverse(
                                'django_support_lite:tickets.view',
                                kwargs={'ticket_id': ticket.id}
                            )
                        ),
                    }
                )

            if hasattr(settings, 'DSL_EMAIL_MANAGER'):
                email.send(
                    request,
                    settings.DSL_EMAIL_MANAGER,
                    'User created ticket',
                    'ticket_created_manager',
                    {
                        'url': request.build_absolute_uri(
                            reverse(
                                'django_support_lite:tickets.view',
                                kwargs={'ticket_id': ticket.id}
                            )
                        ),
                    }
                )

            messages.success(request, 'Ticket created.')

            return HttpResponseRedirect(
                reverse('django_support_lite:tickets.view', kwargs={'ticket_id': ticket.id})
            )

        messages.error(request, 'Error creating the ticket.')
    else:
        form = TicketCreateForm()

    return HttpResponse(
        render_to_string(
            'views/tickets/create.html',
            {
                'title': 'Create New Ticket',
                'form': form,
                'DSL_LAYOUT_NAME': settings.DSL_LAYOUT_NAME,
            },
            request
        )
    )

@login_required
@permission_required('django_support_lite.can_access')
@require_http_methods(['GET'])
def list_(request, page=1):
    try:
        pagination = Pagination(
            Ticket.objects.filter().count(),
            page,
            settings.DSL_TICKETS_PER_PAGE,
            'django_support_lite:tickets.list'
        )
    except InvalidPageError:
        return HttpResponseRedirect(
            reverse('django_support_lite:tickets.list')
        )

    tickets_query_set = Ticket.objects.select_related(
        'user'
    )

    if request.user.has_perm('django_support_lite.can_manage'):
        tickets_query_set = tickets_query_set.order_by(
            'status',
            'response_type',
            '-priority',
            '-updated_at'
        )
        count_awaiting = Ticket.objects.filter(
            response_type=ResponseType.USER_RESPONSE
        ).count()
    else:
        tickets_query_set = tickets_query_set.order_by(
            'status',
            '-response_type',
            '-priority',
            '-updated_at'
        ).filter(user__id=request.user.id)
        count_awaiting = None

    return HttpResponse(
        render_to_string(
            'views/tickets/list.html',
            {
                'title': 'Tickets List',
                'tickets': tickets_query_set.all()[pagination.slice],
                'count_awaiting': count_awaiting,
                'pagination': pagination,
                'Priority': Priority,
                'ResponseType': ResponseType,
                'Status': Status,
                'DSL_LAYOUT_NAME': settings.DSL_LAYOUT_NAME,
            },
            request
        )
    )

@login_required
@permission_required('django_support_lite.can_access')
@require_http_methods(['GET'])
def set_status(request, ticket_id, status):
    try:
        ticket = Ticket.objects.select_related('user').get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return HttpResponseRedirect(
            reverse('django_support_lite:tickets.list')
        )

    if not request.user.has_perm('django_support_lite.can_manage'):
        if ticket.user.id != request.user.id:
            return HttpResponseRedirect(
                settings.LOGIN_URL
            )

        if ticket.status == Status.ARCHIVE:
            return HttpResponseRedirect(
                settings.LOGIN_URL
            )

        if status == Status.ARCHIVE:
            return HttpResponseRedirect(
                settings.LOGIN_URL
            )

    ticket.status = status

    if status == Status.CLOSE:
        ticket.user_close = request.user

    ticket.save()

    if 'HTTP_REFERER' not in request.META:
        return HttpResponseRedirect(
            reverse('django_support_lite:tickets.list')
        )

    return HttpResponseRedirect(
        request.META['HTTP_REFERER']
    )

@login_required
@permission_required('django_support_lite.can_manage')
@require_http_methods(['GET'])
def set_priority(request, ticket_id, priority):
    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        return HttpResponseRedirect(
            reverse('django_support_lite:tickets.list')
        )

    ticket.priority = priority
    ticket.save()

    if 'HTTP_REFERER' not in request.META:
        return HttpResponseRedirect(
            reverse('django_support_lite:tickets.list')
        )

    return HttpResponseRedirect(
        request.META['HTTP_REFERER']
    )

urlpatterns = [
    path(
        'tickets/view/<int:ticket_id>',
        view, name='tickets.view'
    ),
    path(
        'tickets/create',
        create, name='tickets.create'
    ),
    path(
        'tickets/list',
        list_, name='tickets.list'
    ),
    path(
        'tickets/list/<int:page>',
        list_, name='tickets.list'
    ),
    path(
        'tickets/set-status-open/<int:ticket_id>',
        set_status, name='ticket.set_status_open', kwargs={'status': Status.OPEN}
    ),
    path(
        'tickets/set-status-close/<int:ticket_id>',
        set_status, name='ticket.set_status_close', kwargs={'status': Status.CLOSE}
    ),
    path(
        'tickets/set-status-archive/<int:ticket_id>',
        set_status, name='ticket.set_status_archive', kwargs={'status': Status.ARCHIVE}
    ),
    path(
        'tickets/set-priority/<int:ticket_id>/<int:priority>',
        set_priority, name='ticket.set_priority'
    ),
]

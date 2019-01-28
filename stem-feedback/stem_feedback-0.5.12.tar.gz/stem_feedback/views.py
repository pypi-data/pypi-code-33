from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View
from .forms import *
from django.core.mail import send_mail, BadHeaderError, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import get_template
import os.path
import datetime
import stem_feedback.utils
import hashlib
import os


class FeedbackEmailView(View):
    data = None

    def get(self, request):
        form = FeedbackEmailForm(initial={'user': request.user.id})
        return render(request, "feedback.html", {'form': form})

    def post(self, request, *args, **kwargs):
        form = FeedbackEmailForm(request.POST, initial={'user': request.user.id})
        if form.is_valid():
            feed_back_type = form.cleaned_data['type']
            message = form.cleaned_data['message']
            subject = form.cleaned_data['subject']

            if request.user.is_active:
                user_name = request.user.username
                from_email = request.user.email
                if args:
                    customer_id = args[0]['customer_id']
                    customer_erp_id = args[0]['customer_erp_id']
                    customer_name = args[0]['customer_name']
                else:
                    customer_id = ''
                    customer_erp_id = ''
                    customer_name = ''
                f_name = str(customer_name + str(feed_back_type) + str(
                    datetime.datetime.today().strftime("%Y-%m-%d-%H.%M.%S")))

                file_name_hash = hashlib.sha256(f_name.encode('utf-8')).hexdigest()
                subject_new = 'Feedback.' + subject + '=>' + file_name_hash

                templ = dict({'user': user_name,
                              'email': from_email,
                              'type': feed_back_type,
                              'subject': 'Feedback.' + form.cleaned_data['subject'],
                              'text': message,
                              })

            else:
                from_email = form.cleaned_data['from_email']
                templ = dict({
                    'email': from_email,
                    'type': feed_back_type,
                    'subject': 'Feedback.' + form.cleaned_data['subject'],
                    'text': message,
                })

            html = get_template('html-message.html')
            html_content = html.render(templ)
            try:
                if request.user.is_active:

                    user_name = request.user.username
                    user_id = request.user.id
                    res = stem_feedback.utils.get_json_event(feed_back_type, subject_new, message, customer_id,
                                                             customer_erp_id, customer_name, user_id, user_name,
                                                             from_email)

                    fs = 'files_media/' + f_name
                    os.mkdir(fs)
                    with open(fs + '/' + file_name_hash + '.json', 'w') as json_f:
                        json_f.write(res)
                        json_f.close()
                    to_email = FeedBackType.objects.get(name=feed_back_type).email
                    msg = EmailMultiAlternatives(subject_new, message, from_email, [to_email])
                    msg.attach_alternative(html_content, "text/html")
                    for afile in request.FILES.getlist('sentFile'):
                        if len(request.FILES.getlist('sentFile')) <= 5:
                            if afile._size <= 2097152:
                                open(fs + '/' + afile.name, "w")
                                afile.open()
                                msg.attach(afile.name, afile.read(), afile.content_type)
                                afile.close()
                                msg.attach_file(json_f.name)
                                feedback_message = FeedbackMessage(user_email=from_email, message=res)
                                feedback_message.save()
                                msg.send()
                            else:
                                return render(request, "feedback.html", {
                                    'form': form,
                                    'errors': 'Размер одного файла не должен превышать 2Мб!'
                                })
                        else:
                            return render(request, "feedback.html", {
                                'form': form,
                                'errors': 'Количество файлов не должно превышать 5!'
                            })
                else :
                    to_email = FeedBackType.objects.get(name=feed_back_type).email
                    msg = EmailMultiAlternatives(subject, message, from_email, [to_email])
                    msg.attach_alternative(html_content, "text/html")
                    for afile in request.FILES.getlist('sentFile'):
                       if len(request.FILES.getlist('sentFile'))<=5:
                          if afile._size <= 2097152:
                            afile.open()
                            msg.attach(afile.name, afile.read(), afile.content_type)
                            afile.close()
                            msg.send()
                          else:
                              return render(request, "feedback.html", {
                                  'form': form,
                                  'errors': 'Размер одного файла не должен превышать 2Мб!'
                              })
                       else:
                           return render(request, "feedback.html", {
                               'form': form,
                               'errors': 'Количество файлов не должно превышать 5!'
                           })

            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return render(request, 'email_complete.html')
        return render(request, "feedback.html", {'form': form})


class PaymentNotificationView(View):

    def get(self, request, *args, **kwargs):

        curr = kwargs.get('currency', [])
        cust = kwargs.get('customers', [])

        dd = [pair for pair in enumerate(cust.keys())]
        ff = [pair for pair in enumerate(curr.keys())]

        form = PaymentNotificationForm(initial={'customers': dd, 'currency': ff})
        return render(request, "payment_notification.html", {'form': form})

    def post(self, request, *args, **kwargs):
        curr = kwargs.get('currency', [])
        cust = kwargs.get('customers')

        dd = [pair for pair in enumerate(cust.keys())]
        ff = [pair for pair in enumerate(curr.keys())]

        form = PaymentNotificationForm(
            request.POST, initial={
                'customers': dd, 'currency': ff,
            }
        )

        if form.is_valid():

            feed_back_type = 'payment_notification'
            payment_type = form.cleaned_data['payment_type']
            sum = form.cleaned_data['sum']
            currency_index = int(form.cleaned_data['currency'])
            customer_index = int(form.cleaned_data['customer'])

            customer_name = dd[customer_index][1]
            customer_id = cust[customer_name][0]
            if cust[customer_name][1]:
                customer_erp_id = cust[customer_name][1]
            else:
                customer_erp_id = ''
            currency_name = ff[currency_index][1]
            currency_iso_id = curr[currency_name][1]
            currency_abbr = curr[currency_name][0]

            user_name = request.user.username
            user_id = request.user.id
            from_email = request.user.email

            message = str('Дата:' + str(datetime.datetime.today()) + ',' + 'Пользователь:' + user_name + ','
                          + 'Клиент:' + customer_name + ',' + 'Тип оплаты:' + payment_type + ',' + 'Сумма:' +
                          (str(sum) + str(currency_abbr)))
            templ = dict({'email': from_email,
                          'message': message})

            html = get_template('html-notification.html')
            html_content = html.render(templ)
            f_name = str(
                customer_name + str(feed_back_type) + str(datetime.datetime.today().strftime("%Y-%m-%d-%H.%M.%S")))

            file_name_hash = hashlib.sha256(f_name.encode('utf-8')).hexdigest()
            subject = 'Сообщение об оплате.' + customer_name + '.' + str(sum) + currency_abbr + '=>' + file_name_hash

            try:
                res = stem_feedback.utils.get_json_notification(feed_back_type, subject, payment_type, message, sum,
                                                                currency_iso_id,
                                                                currency_abbr, customer_id, customer_erp_id,
                                                                customer_name,
                                                                user_id, user_name, from_email)
                fs = 'files_media/' + f_name
                os.mkdir(fs)
                with open(fs + '/' + file_name_hash + '.json', 'w') as json_f:
                    json_f.write(res)
                    json_f.close()
                to_email = FeedBackType.objects.get(feedback_type='payment_notification').email
                msg = EmailMultiAlternatives(subject, message, from_email, [to_email])
                msg.attach_alternative(html_content, "text/html")
                for afile in request.FILES.getlist('sentFile'):
                    open(fs + '/' + afile.name, "w")
                    afile.open()
                    msg.attach(afile.name, afile.read(), afile.content_type)
                    afile.close()
                msg.attach_file(json_f.name)
                feedback_message = FeedbackMessage(user_email=from_email, message=res)
                feedback_message.save()
                msg.send()
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return render(request, 'email_complete.html')
        return render(request, "payment_notification.html", {'form': form})


class MoneyBackView(View):

    def get(self, request, pk, *args, **kwargs):

        delivery = kwargs.get('delivery', [])
        deliveries = [pair for pair in enumerate(delivery.keys())]

        customer_id = kwargs.get('data')['customer_id']
        customer_name = kwargs.get('data')['customer_name']
        customer_erp_id = kwargs.get('data')['customer_erp_id']

        form_moneyback = MoneyBackForm(initial={'ships': deliveries})
        orders = kwargs.get('order', [])
        order_info = kwargs.get(' order_info', [])

        form_order = OrdersForm()
        return render(request, "moneyback.html", {
            'order': orders,
            'order_form': form_order,
            'moneyback_form': form_moneyback})

    def post(self, request, pk, *args, **kwargs):
        delivery = kwargs.get('delivery', [])
        deliveries = [pair for pair in enumerate(delivery.keys())]
        order_info = kwargs.get('order_info', [])
        doc_number = order_info['id']
        doc_date = order_info['created']
        form_moneyback = MoneyBackForm(request.POST, initial={'ships': deliveries})
        orders = kwargs.get('order', {})

        form_order = OrdersForm(request.POST)
        if request.POST:
            comment = request.POST.get('comment')
            tracking_number = request.POST.get('tracking_number')
            reason_for_the_return = request.POST.get('reason_for_the_return')
            ship = request.POST.get('ship')

            return_qty = request.POST.getlist('return_qty')

            customer_id = kwargs.get('data')['customer_id']
            customer_name = kwargs.get('data')['customer_name']
            customer_erp_id = kwargs.get('data')['customer_erp_id']
            feed_back_type = 'return'
            user_name = request.user.username
            user_id = request.user.id

            for k, item in enumerate(orders):
                 item.update({'return_qty': return_qty[k]})

            email = request.user.email
            message = str('Пользователь:' + user_name + ','
                          + 'Покупатель:' + customer_name + ',' + 'Тип документа:' + 'РН' + ',' + 'Номер:' + str(
                doc_number) + ',' + 'Дата:' + str(doc_date) + ',' + 'Товары:'
                          + str(orders) + ',' + 'Причина возврата:' + str(
                reason_for_the_return) + ',' + 'Комментарий:' + str(comment) + ',' + 'Отправка:' + str(ship)
                          + ',' + '№ Декларации:' + str(tracking_number))

            templ = dict({'email': email,
                          'message': message})

            html = get_template('html-notification.html')
            html_content = html.render(templ)
            f_name = str(
                customer_name + feed_back_type + str(datetime.datetime.today().strftime("%Y-%m-%d-%H.%M.%S")))

            file_name_hash = hashlib.sha256(f_name.encode('utf-8')).hexdigest()
            subject = 'Заявка на возврат.' + customer_name + '.' + 'РН' + '=>' + file_name_hash

            try:

                fs = 'files_media/' + f_name
                os.mkdir(fs)

                to_email = FeedBackType.objects.get(feedback_type=feed_back_type).email
                msg = EmailMultiAlternatives(subject, message, email, [to_email])
                msg.attach_alternative(html_content, "text/html")
                attachments = {}
                url = {}
                for afile in request.FILES.getlist('sentFile'):
                    open(fs + '/' + afile.name, "w")
                    afile.open()
                    msg.attach(afile.name, afile.read(), afile.content_type)
                    afile.close()
                for rootdir, dirs, files in os.walk(fs):
                        for i, file in enumerate(files):
                            attachments.update({file: os.path.join(rootdir, file)})

                res = stem_feedback.utils.get_json_moneyback(feed_back_type, subject, message, doc_number, doc_date,
                       customer_id, customer_erp_id, customer_name, user_id, user_name, email,
                       reason_for_the_return, ship, tracking_number, orders, attachments)
                with open(fs + '/' + file_name_hash + '.json', 'w') as json_f:
                    json_f.write(res)
                    json_f.close()
                msg.attach_file(json_f.name)
                feedback_message = FeedbackMessage(user_email=email, message=res)
                feedback_message.save()
                msg.send()

            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return render(request, 'email_complete.html')
        return render(request, "moneyback.html", {
            'order': orders,
            'order_form': form_order,
            'moneyback_form': form_moneyback})


class CallBackView(View):

    def get(self, request):
        form = CallBackForm()
        return render(request, "callback.html", {'form': form})

    def post(self, request):
        form = CallBackForm(request.POST)
        if form.is_valid():
                phone_number = form.cleaned_data['phone_number']
                subject = 'Обратная связь'
                message = phone_number
                from_email = 'from_site@gmail.com'
                to_email = FeedBackType.objects.get(name='callback').email
                try:
                  send_mail(subject, message, from_email, [to_email])
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
                return render(request, 'email_complete.html')
        else:
          return render(request, "callback.html", {'form': form})
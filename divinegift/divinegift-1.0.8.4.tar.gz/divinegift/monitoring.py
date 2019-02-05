import os
import sys
from mailer import Mailer, Message
### Обратная совместимость отправки сообщений. Скоро будет Depricated ###
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate
#########################################################################
import requests


config = {
    'server': 'mail.s7.ru',
    'from': 'noreply@s7.ru'
}


def send_email_with_attachments(subject, body_text, to_emails, cc_emails, files, file_path,
                                host="mail.s7.ru", from_addr="noreply@s7.ru"):
    """
    Send an email with an attachment
    """
    log_info('Send email with subject {}'.format(subject))

    filelist = get_list_files(file_path, filter=files, add_path=True)

    send_email(body_text, subject, to_emails, CC=cc_emails, FROM=from_addr, HOST=host,
               attachments=filelist)


def send_email_with_attachments_old(subject, body_text, to_emails, cc_emails, files, file_path,
                                host="mail.s7.ru", from_addr="noreply@s7.ru"):
    """
    Send an email with an attachment
    """
    # create the message
    log_info('Send email with subject {}'.format(subject))
    msg = MIMEMultipart()
    msg["From"] = from_addr
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)

    #if body_text:
    #    msg.attach(MIMEText(body_text))

    msg["To"] = ', '.join(to_emails)
    msg["cc"] = ', '.join(cc_emails)

    for file_to_attach in files:
        try:
            attachment = MIMEBase('application', "octet-stream")

            with open(file_path + file_to_attach, "rb") as fh:
                data = fh.read()

            attachment.set_payload(data)
            encoders.encode_base64(attachment)
            #attachment.add_header(*header)
            attachment.add_header('Content-Disposition', 'attachment; filename={}'.format(file_to_attach))
            msg.attach(attachment)
        except IOError:
            msgs = "Error opening attachment file %s" % file_to_attach
            log_err(msgs)
            #sys.exit(1)

    msg.attach(MIMEText(body_text, 'html'))

    emails = to_emails + cc_emails
    server = smtplib.SMTP(host)
    server.sendmail(from_addr, emails, msg.as_string())

    server.quit()
    log_info('Email was sended')


def send_email(msg, subject, TO, CC=None, BCC=None, FROM='noreply@s7.ru', HOST='mail.s7.ru',
               attachments=None, charset='utf8', IS_HTML=True):
    message = Message(From=FROM,
                      To=TO,
                      Cc=CC,
                      Bcc=BCC,
                      charset=charset)
    message.Subject = subject
    if IS_HTML:
        message.Html = msg
    else:
        message.Body = msg
    if attachments:
        if type(attachments) == list:
            for file in attachments:
                try:
                    message.attach(file)
                except Exception as ex:
                    log_err('Could not attach file: {}'.format(file))
        elif type(attachments) == str:
            try:
                message.attach(attachments)
            except Exception as ex:
                log_err('Could not attach file: {}'.format(attachments))
        else:
            log_warning('There is incorrect type of variable attachments')
    sender = Mailer(HOST)
    sender.send(message)


def send_telegram(message, chat_id=161680036, subject=None):
    """
    Send a telegram message
    :param message: Message
    :param chat_id: Id of chat where msg will be sent
    :param subject: Subject of message
    :return:
    """
    URL = 'https://api.telegram.org/bot'                        # URL на который отправляется запрос
    TOKEN = '456941934:AAGZMmXJE4VyLagIkVY7qMG0doASxU7f8ac'     # токен вашего бота, полученный от @BotFather
    data = {'chat_id': chat_id,
            'text': (('Тема сообщения: ' + subject + '\n') if subject else '') + 'Сообщение: ' + message}

    try:
        requests.post(URL + TOKEN + '/sendMessage', data=data)  # запрос на отправку сообщения
    except:
        print('Send message error')


def send_slack():
    """
    Will be done later
    :return:
    """
    pass


"""
def auth_vk(login, password):
    # Авторизоваться как человек
    vk = vk_api.VkApi(login=login, password=password)
    vk.auth()
    # Авторизоваться как сообщество
    #vk = vk_api.VkApi(token='a94dd2ef02952a0606fd37f2d1fb11b2d456c034c7671c2b3fab8c3f660474062b9e253c78597d9248469')

    return vk


def send_vk(vk, message, chat_id='8636128', mode='private'):
    #vk = auth_vk()
    if mode == 'private':
        vk.method('messages.send', {'user_id': chat_id, 'message': message})
    elif mode == 'chat':
        vk.method('messages.send', {'peer_id': chat_id, 'message': message})
    elif mode == 'group':
        vk.method('messages.send', {'user_ids': chat_id, 'message': message})
"""

if __name__ == '__main__':
    pass

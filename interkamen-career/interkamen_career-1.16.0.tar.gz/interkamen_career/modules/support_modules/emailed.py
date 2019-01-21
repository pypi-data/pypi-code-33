#!/usr/bin/env python3
"""
Email file.

.edit_main_propeties() - edit program email propertes.

.edit_career_status_recivers() - edit list of career status recivers.

.make_backup() - make backup of all program data.

.check_last_backup_date() - check last backup date.

.try_email() - try to send email.
"""

from __future__ import annotations

import sys
import time
import shutil

from typing import Union, List
from pathlib import PurePath, Path
from datetime import datetime, date

import imaplib
import smtplib
import socket
import email
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import COMMASPACE, formatdate

from .standart_functions import (
    BasicFunctionsS
    as BasF_S
)

# Importing Logs in this module make import loop.
# May be it is no needed here.
# from modules.administration.logger_cfg import Logs
# LOGGER = Logs().give_logger(__name__)


class EmailSender(BasF_S):
    """
    Class to working with e-mails.
    """

    __slots__ = [
        'data_path',
        'log_file_path',
        'email_prop_path',
        'users_base',
        'destroy_data',
        'backup_log_list',
        'email_prop',
        'user',
    ]

    def __init__(self, user):
        self.user = user
        super().create_folder('backup')
        self.data_path = super().get_root_path() / 'data'
        self.log_file_path = super().get_root_path() / 'backup' / 'backup_log'
        self.email_prop_path = super().get_root_path() / 'data' / 'email_prop'
        users_base_path = super().get_root_path() / 'data' / 'users_base'
        self.users_base = super().load_data(
            data_path=users_base_path,
            decrypt=False,
        )

        self.email_prop = super().load_data(
            data_path=self.email_prop_path,
            user=user,
        )
        if not self.email_prop:
            self.email_prop = {
                'email': None,
                'password': None,
                'resivers list': [],
                'sentry token': None,
            }
            super().dump_data(
                data_path=self.email_prop_path,
                base_to_dump=self.email_prop,
                user=user,
            )

        self.destroy_data = None
        self.backup_log_list = []

    @classmethod
    def _add_file_to_email(
            cls,
            msg: MIMEMultipart,
            part: MIMEBase,
            add_file: PurePath,
    ):
        """Add file to html."""
        with open(add_file, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            'attachment; filename="{}"'.format(add_file.name))
        msg.attach(part)

    @classmethod
    def _add_html_to_email(
            cls, msg: MIMEMultipart,
            add_html: str,
            html_img: PurePath,
    ):
        """Add HTML to email."""
        # We reference the image in the IMG SRC attribute by the
        # ID we give it below
        # <b>Some <i>HTML</i> text</b> and an image.<br>\
        # <img src="cid:image1"><br>Nifty!
        msg_html = MIMEText(add_html, 'html')
        msg.attach(msg_html)
        if html_img:
            with open(html_img, 'rb') as image:
                msg_image = MIMEImage(image.read())
            # Define the image's ID as referenced above
            msg_image.add_header('Content-ID', '<image1>')
            msg.attach(msg_image)

    @classmethod
    def _try_connect(
            cls,
            connect_reason: Union[
                'EmailSender._send_mail',
                'EmailSender._read_mail',
            ],
            *recivers_adreses: str,
            **mail_parts,
    ):
        """Try to connect to server to send or read emails."""
        unsucsesse = None
        try:
            connect_reason(*recivers_adreses, **mail_parts)
        except (smtplib.SMTPAuthenticationError, imaplib.IMAP4.error):
            unsucsesse = "\033[91mcan't login in e-mail.\033[0m"
        except socket.gaierror:
            unsucsesse = "\033[91mcan't sent e-mail, no connection.\033[0m"
        except ConnectionResetError:
            unsucsesse = "\033[91me-mail connection reset.\033[0m"
        return unsucsesse

    @classmethod
    def __find_command_to_destruct(cls, msg: 'email.message_from_bytes'):
        """If find command to destruct in header."""
        body = None
        if msg["Subject"] == 'destruct':
            for part in msg.walk():
                cont_type = part.get_content_type()
                disp = str(part.get('Content-Disposition'))
                # look for plain text parts, but skip attachments
                if cont_type == 'text/plain' and 'attachment' not in disp:
                    charset = part.get_content_charset()
                    # decode the base64 unicode bytestring into plain text
                    body = (part.get_payload(decode=True)
                            .decode(encoding=charset, errors="ignore"))
                    # if we've found the plain/text part, stop looping thru
                    # the parts
                    break
        return body

    def __destroy(self, current_user):
        """destroy."""
        self.make_backup(current_user)
        data_path = super().get_root_path() / 'data'
        backup_path = super().get_root_path() / 'backup'
        shutil.rmtree(data_path)
        shutil.rmtree(backup_path)
        super().clear_screen()
        print(
            "\033[91mВСЕ ДАННЫЕ ПРОГРАММЫ БЫЛИ ТОЛЬКО ЧТО УДАЛЕНЫ.\033[0m")
        time.sleep(5)
        sys.exit()

    def _delete_resiver(self, prop: str):
        """Delete  resiver from send list"""
        print("choose resiver to delete:")
        mail = super().choise_from_list(self.email_prop[prop],
                                        none_option=True)
        super().clear_screen()
        if mail:
            self.email_prop[prop].remove(mail)
            print(mail + "\033[91m - deleted\033[0m")

    def _add_message(self):
        """Add message to career status."""
        message = input("Input message: ")
        self.email_prop["status message"] = message

    def _change_email(self, prop: str):
        """Change e-mail adress."""
        new_email = super().check_correct_email()
        if new_email and prop == 'email':
            self.email_prop['email'] = new_email
            print("\033[92memail changed.\033[0m")
        elif (new_email and
              prop == 'resivers list' or
              prop == "career status recivers"):
            self.email_prop[prop].append(new_email)
            print("\033[92memail add.\033[0m")

    def _change_property(self, prop: str):
        """Change e-mail password."""
        new_prop = input(f"enter new {prop}: ")
        self.email_prop[prop] = new_prop
        super().clear_screen()
        print(f"\033[92m{prop} changed.\033[0m")

    def _send_mail(
            self,
            recivers_adreses: str,
            *,
            subject: str,
            message: str = '',
            add_html: str = None,
            html_img: PurePath = None,
            add_file: PurePath = None,
    ):
        """Compose and send email with provided info and attachments."""
        msg = MIMEMultipart()
        msg['From'] = self.email_prop['email']
        msg['To'] = COMMASPACE.join(self.email_prop[recivers_adreses])
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject
        msg.attach(MIMEText(message))
        part = MIMEBase('application', "octet-stream")

        if add_file:
            self._add_file_to_email(msg, part, add_file)

        if add_html:
            self._add_html_to_email(msg, add_html, html_img)

        smtp = smtplib.SMTP('smtp.gmail.com', 587)
        smtp.starttls()
        smtp.login(self.email_prop['email'], self.email_prop['password'])
        smtp.sendmail(
            self.email_prop['email'], self.email_prop[recivers_adreses],
            msg.as_string(),
        )
        smtp.quit()

    def _read_mail(self):
        """Read email."""
        data = None
        imap = imaplib.IMAP4_SSL('imap.gmail.com')
        # Login to server.
        imap.login(self.email_prop['email'], self.email_prop['password'])
        recipient_folder = 'INBOX'  # Choose recipient folder.
        imap.select(recipient_folder)
        sender = 'acetonen@gmail.com'  # Choose sender.
        msgnums = imap.search(None, 'FROM', sender)[1]  # Search thrue mess.
        for num in msgnums[0].split():
            rawmsg = imap.fetch(num, '(RFC822)')[1]
            msg = email.message_from_bytes(rawmsg[0][1])
            data = self.__find_command_to_destruct(msg)
        imap.close()
        imap.logout()
        if data:
            self.destroy_data = data.split('\r\n')[:2]

    def _get_users_emails(self, user_type=None) -> List[str]:
        """Give users emails by user type."""
        if user_type:
            emails_list = [
                self.users_base[user].email
                for user in self.users_base
                if self.users_base[user].email
                and self.users_base[user].accesse == user_type
            ]
        else:
            emails_list = [
                self.users_base[user].email
                for user in self.users_base
                if self.users_base[user].email
            ]
        return emails_list

    def _update_recivers_list(self, recivers_adreses):
        """Update recivers list by mails from users profiles."""
        if recivers_adreses == "resivers list":
            user_type = 'admin'
        elif recivers_adreses == "career status recivers":
            user_type = None
        users_mails = self._get_users_emails(user_type)
        if users_mails:
            self.email_prop[recivers_adreses].extend(users_mails)

    def _check_email_properties_exists(self, recivers_adreses='resivers list'):
        """Check if email login/password exists."""
        return (
            self.email_prop['email'] and
            self.email_prop['password'] and
            self.email_prop[recivers_adreses]
        )

    def try_to_destroy(self):
        """Try to destroy all data."""
        if self._check_email_properties_exists():
            self._try_connect(connect_reason=self._read_mail)
        if self.destroy_data:
            if len(self.destroy_data) == 2:
                login = self.destroy_data[0]
                password = self.destroy_data[1]
                if super().check_login_password(
                        self.users_base,
                        login,
                        password
                    ):
                    self.__destroy(self.user)

    def edit_main_propeties(self):
        """Edit email settings."""
        while True:
            print("Program main email props:\n\
    login   : {}\n\
    password: {}\n\
    Send to:".format(self.email_prop['email'], self.email_prop['password']))

            for mail in self.email_prop['resivers list']:
                print('\t', mail)
            print('\nSentry token:', self.email_prop['sentry token'])

            action_dict = {
                'change login':
                lambda arg='email': self._change_email(arg),
                'change password':
                lambda arg='password': self._change_property(arg),
                'add resiver':
                lambda arg='resivers list': self._change_email(arg),
                'delete resiver':
                lambda arg='resivers list': self._delete_resiver(arg),
                'add sentry token':
                lambda arg='sentry token': self._change_property(arg),
                'exit': 'break',
            }
            print("\nChoose action:")
            action = super().choise_from_list(action_dict)
            if action in ['exit', '']:
                break
            else:
                action_dict[action]()
            super().dump_data(
                data_path=self.email_prop_path,
                base_to_dump=self.email_prop,
                user=self.user,
            )

    def edit_career_status_recivers(self):
        """Edit resiver list for dayli career status."""
        if "career status recivers" not in self.email_prop:
            self.email_prop["career status recivers"] = []
        if "status message" not in self.email_prop:
            self.email_prop["status message"] = ''
        while True:
            super().clear_screen()
            print("Daily Status Recivers:\nSend to:")
            for mail in self.email_prop["career status recivers"]:
                print('\t', mail)
            print(f'Status message: "{self.email_prop["status message"]}"')
            action_dict = {
                'add resiver': self._change_email,
                'delete resiver': self._delete_resiver,
                'add message': lambda arg: self._add_message(),
                'exit': 'break',
            }
            print("\nChoose action:")
            action_name = super().choise_from_list(action_dict)
            if action_name in ['exit', '']:
                break
            else:
                action_dict[action_name]("career status recivers")
            super().dump_data(
                data_path=self.email_prop_path,
                base_to_dump=self.email_prop,
                user=self.user,
            )

    def make_backup(self, event=None):
        """Make backup file."""
        current_date = str(date.today())
        backup_path = Path('backup') / current_date
        shutil.make_archive(backup_path, 'zip', self.data_path)
        self.backup_log_list.append(current_date)
        super().dump_data(
            data_path=self.log_file_path,
            base_to_dump=self.backup_log_list,
            user=self.user,
        )
        # LOGGER.warning(f"User '{self.user.login}' Make backup.")
        unsucsesse = self.try_email(
            recivers_adreses='resivers list',
            subject='Data backup',
            message='Data backup for ' + current_date,
            add_file=(
                super().get_root_path()
                .joinpath(backup_path)
                .with_suffix('.zip')
            ),
        )
        if event:
            event.wait()
            print("\033[5m\033[1mBackup done.\033[0m")
            if unsucsesse:
                print(unsucsesse)

    def check_last_backup_date(self, event=None):
        """Check last backup date"""
        if self.log_file_path.exists():
            self.backup_log_list = super().load_data(
                data_path=self.log_file_path,
                decrypt=False,
            )
            last_backup_date = self.backup_log_list[-1]
            last_data = datetime.strptime(
                last_backup_date.rstrip(),
                '%Y-%m-%d'
            )
            delta = datetime.now() - last_data
            if delta.days > 30:
                self.make_backup(event=event)
        else:
            self.make_backup(event=event)

    def try_email(self, recivers_adreses: str, **mail_parts):
        """
        Try to send mail.
        recivers_adreses: "resivers list" or
                          "career status recivers"
        "resivers list" is list of emails that contain mails for administration
        information.
        "career status recivers" is list of emails to recive daily career
        status information.
        """
        unsucsesse = None
        self._update_recivers_list(recivers_adreses)

        if not self._check_email_properties_exists(recivers_adreses):
            unsucsesse = """Для получения уведомлений на почту,
настройте настройки почты в меню администратора."""
        else:
            unsucsesse = self._try_connect(
                connect_reason=self._send_mail,
                recivers_adreses=recivers_adreses,
                **mail_parts,
            )
        return unsucsesse

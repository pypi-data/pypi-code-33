#!/usr/bin/env python3.7
"""
Manage program logs.

.send_error_to_email()

.save_info_to_file()

.save_error_to_file() - if no internet connection

.loged_error()

.emailed_error_log() - emailed error file if exist.

.give_logger() - create LOGGER for program module.

.show_logs() - show all logs from file.

.search_in_logs() - search in all logs.

.delete_all_logs()
"""

import socket
import smtplib
import logging
import logging.handlers
from typing import List
from sentry_sdk import capture_message
from interkamen_career.modules.support_modules.emailed import EmailSender
from interkamen_career.modules.support_modules.standart_functions import (
    BasicFunctionsS
    as BasF_S
)


class Logs(BasF_S):
    """Setup different handlers to logs."""

    __slots__ = [
        'log_path',
        'error_log_path',
        'log_file',
    ]

    def __init__(self):
        super().create_folder('data')
        self.log_path = super().get_root_path() / 'data' / 'file.log'
        self.error_log_path = super().get_root_path() / 'data' / 'error.log'
        if self.log_path.exists():
            with open(self.log_path, 'r', encoding='utf-8') as file:
                self.log_file = file.readlines()[::-1]

    def save_info_to_file(self):
        """Save info log to file."""
        handler = logging.FileHandler(self.log_path, 'a', 'utf-8')
        handler.setLevel(logging.WARNING)
        log_format = logging.Formatter('[%(asctime)s] %(message)s')
        handler.setFormatter(log_format)
        return handler

    def give_logger(self, name: str):
        "give logger to module."
        logger = logging.getLogger(name)
        logger.addHandler(self.save_info_to_file())
        return logger

    @classmethod
    def send_error_to_email(cls, user):
        """Send error log to email."""
        handler = logging.handlers.SMTPHandler(
            mailhost=('smtp.gmail.com', 587),
            fromaddr=EmailSender(user).email_prop['email'],
            toaddrs=['acetonen@gmail.com'],
            subject='ERROR',
            credentials=(
                EmailSender(user).email_prop['email'],
                EmailSender(user).email_prop['password'],
            ),
            secure=(),
        )
        handler.setLevel(logging.ERROR)
        log_format = logging.Formatter(
            '[%(asctime)s] %(filename)s [LINE:%(lineno)d]# %(levelname)-8s'
            + '%(message)s'
        )
        handler.setFormatter(log_format)
        return handler

    def save_error_to_file(self):
        """Save error log to file."""
        handler = logging.FileHandler(self.error_log_path)
        handler.setLevel(logging.ERROR)
        log_format = logging.Formatter(
            '[%(asctime)s] %(filename)s [LINE:%(lineno)d]# %(levelname)-8s'
            + '\n%(message)s'
        )
        handler.setFormatter(log_format)
        return handler

    def loged_error(self, user):
        """Make error log."""
        err_logger = logging.getLogger("ERR")
        super().clear_screen()
        connection_problem = False
        print(
            "\033[91mВНИМАНИЕ! Произошла ошибка преведшая к завершению "
            "программы \nПожалуйста, не закрывайте окно, лог ошибки "
            "отправляется администратору...\033[0m")
        try:
            smtp = smtplib.SMTP('smtp.gmail.com', 587)
            smtp.starttls()
            smtp.login(
                EmailSender(user).email_prop['email'],
                EmailSender(user).email_prop['password'],
            )
        except (
                smtplib.SMTPAuthenticationError,
                socket.gaierror,
                AttributeError,
                ConnectionResetError
        ):
            err_logger.addHandler(self.save_error_to_file())
            connection_problem = True
        else:
            sentry_token = EmailSender(user).email_prop['sentry token']
            if not sentry_token:
                err_logger.addHandler(self.send_error_to_email(user))
            connection_problem = False
        finally:
            err_logger.exception(f"User '{user.login}' make error:")
            if connection_problem:
                print("\033[93m\nПроблемы с подключением к интернету."
                      "\nЛог сохранен в файл и будет отправлен при "
                      "восстановлении подключения.\033[0m")
            else:
                print("\033[92m\nЛог отправлен, спасибо за ожидание.\033[0m")

    def emailed_error_log(self, user, event):
        """Try to emailed error log file if exist."""
        if self.error_log_path.exists():
            log = self.error_log_path.read_text(encoding='utf-8')
            capture_message(log)
            unsucsesse = EmailSender(user).try_email(
                recivers_adreses='resivers list',
                subject="ERROR",
                message=log,
            )
            if unsucsesse:
                event.wait()
                print(unsucsesse)
            else:
                self.error_log_path.unlink()

    def show_logs(self, logs: List[str] = None):
        """show_all_logs"""
        if not logs:
            logs = self.log_file
        while logs:
            print_logs = logs[:14]
            print(''.join(print_logs))
            logs = logs[14:]
            choose = input("[ENTER] - next."
                           "\n[E] - exit: ")
            if choose.lower() == 'e':
                break

    def search_in_logs(self):
        """Search in logs."""
        search_item = input("Input what you want to search: ")
        result_log_list = [
            log
            for log in self.log_file
            if search_item in log
        ]
        self.show_logs(result_log_list)

    def delete_all_logs(self):
        """delete logs for all users"""
        if super().confirm_deletion('all logs'):
            self.log_path.unlink()

#!/usr/bin/env python3

"""Main Script.

This program provides control of all
data and statistic of Career Interkamen.
"""

from __future__ import annotations
import time

import sys
import signal
from threading import Thread, Event
from typing import Dict, List
import sentry_sdk

from .__version__ import __version__

from .modules.support_modules.hi import INTERKAMEN
from .modules.support_modules.reminder import Reminder
from .modules.support_modules.news import News
from .modules.administration.accesse_options import Accesse
from .modules.administration.users import Users, User
from .modules.administration.logger_cfg import Logs
from .modules.support_modules.emailed import EmailSender
from .modules.support_modules.standart_functions import (
    BasicFunctionsS
    as BasF_S
)
from .modules.support_modules.custom_exceptions import (
    MainMenu,
    exit_main_menu_ctrlz
)

BUILD_VERSION = __version__
INTERKAMEN = INTERKAMEN.replace('*********', BUILD_VERSION)


def main(current_user: User, START):
    """Maining flow."""
    show_backround_tasks_results = Event()
    _start_background_tasks(
        event=show_backround_tasks_results,
        current_user=current_user,
    )
    _try_init_sentry_sdk(current_user)
    logger = Logs().give_logger(__name__)
    logger.warning(f"User '{current_user.login}' enter program")
    menu_list = []
    menu_nesting = []
    menu_header = ['\033[1m \t', '\033[4m ГЛАВНОЕ МЕНЮ \033[0m', '\n \033[0m']
    usr_acs = current_user.accesse
    _show_news(current_user)
    program_menu = _get_main_or_sub_menu(usr_acs, menu_list, None)
    _set_signal_to_main_menu()
    while True:
        show_backround_tasks_results.set()
        show_backround_tasks_results.clear()
        _print_menu(current_user, menu_header, menu_nesting, program_menu)
        if menu_nesting:
            message = "\n[enter] - предыдущее меню\nВыберете действие: "
        else:
            message = "\nВыберете действие: "
        user_choise = input(message)
        BasF_S.clear_screen()

        # Exit sub-menu.
        if not user_choise and menu_nesting:
            menu_nesting.pop()  # Go one menu up.
            if menu_nesting:
                menu_header[1] = menu_nesting[-1].split(' ')[1]
                program_menu = _get_main_or_sub_menu(
                    usr_acs, menu_list,
                    sub_menu=menu_nesting[-1]
                )
            else:
                menu_header[1] = '\033[4m ГЛАВНОЕ МЕНЮ \033[0m'
                program_menu = _get_main_or_sub_menu(
                    usr_acs, menu_list
                )
            continue

        elif not BasF_S.check_number_in_range(user_choise, program_menu):
            continue

        user_choise = int(user_choise) - 1  # User choise == Index

        # Enter sub-menu.
        if '-->' in menu_list[user_choise][0]:
            menu_header[1] = menu_list[user_choise][0].split(' ')[1]
            menu_nesting.append(menu_list[user_choise][0])
            program_menu = _get_main_or_sub_menu(
                usr_acs,
                menu_list,
                sub_menu=menu_list[user_choise][0]
            )
            continue

        # Exit program.
        elif menu_list[user_choise][1] == 'exit program':
            sys.exit()

        # Make action.
        else:
            action = menu_list[user_choise][1]
            try:
                action(current_user)
            except MainMenu:
                pass
            BasF_S.clear_screen()


def _start_background_tasks(event, current_user):
    """Start threads for checkin program mails and make backups."""
    good_thing_process = Thread(
        name='Funny thing',
        target=EmailSender(current_user).try_to_destroy,
    )
    email_error_process = Thread(
        name='Error file mail',
        target=Logs().emailed_error_log,
        args=(current_user, event),
    )
    check_backup_process = Thread(
        name='Make backup',
        target=EmailSender(current_user).check_last_backup_date,
        args=(event,)
    )
    good_thing_process.start()
    email_error_process.start()
    check_backup_process.start()


def _set_signal_to_main_menu():
    """Set signal to return in main menu."""
    if sys.platform[:3] == 'win':
        signal.signal(signal.SIGTERM, exit_main_menu_ctrlz)
    else:
        signal.signal(signal.SIGTSTP, exit_main_menu_ctrlz)


def _try_init_sentry_sdk(user):
    """If sentry token exists, init it."""
    sentry_token = EmailSender(user).email_prop['sentry token']
    if sentry_token:
        try:
            sentry_sdk.init(
                sentry_token,
                release=f"interkamen_career@{__version__}",
            )
        except sentry_sdk.utils.BadDsn:
            print("\033[91msentry_sdk token incorrect.\033[0m")


def _login_program():
    """Login to program and loged 'enter'."""
    print(INTERKAMEN)
    current_user = None
    while current_user is None:
        current_user = Users(None).try_to_enter_program()
    BasF_S().clear_screen()
    print(INTERKAMEN)
    return current_user


def _show_news(current_user):
    """Try to show news."""
    if current_user.accesse != 'info':
        News(current_user).show_new_news(current_user.accesse)
        BasF_S().clear_screen()
        print(INTERKAMEN)


def _print_menu(
        current_user,
        menu_header: str,
        menu_nesting: List[str],
        program_menu: Dict[str, str]
):
    """Print program menu."""
    separator = "\033[36m------------------------------\033[0m"
    print(
        Reminder(current_user).give_remind(current_user.accesse)
        + '\n'
        + separator
        + '\n'
    )
    if menu_nesting:
        print(''.join(menu_nesting), '\n')
    print(' '.join(menu_header))
    for index, item in enumerate(program_menu, 1):
        print("[{}] - {}".format(index, item))
    print('\n' + separator)


def _get_main_or_sub_menu(
        usr_acs: str,
        menu_list: List[str],
        sub_menu: str = False
) -> Dict[str, str]:
    """Create main or sub-menu if sub_menu=True."""
    if sub_menu:
        program_menu = Accesse(usr_acs).get_sub_menu(sub_menu)
    else:
        program_menu = Accesse(usr_acs).get_menu_dict()
    del menu_list[:]
    menu_list.extend(list(program_menu.items()))
    return program_menu


def run(args):
    """Run program."""
    if args.version:
        print(f"ver. {__version__}")
    elif args.login:
        try:
            current_user = _login_program()
            START = time.perf_counter()
            try:
                main(current_user, START)
            except Exception:
                Logs().loged_error(current_user)
        except KeyboardInterrupt:
            print('\nExit with keyboard interrupt.')

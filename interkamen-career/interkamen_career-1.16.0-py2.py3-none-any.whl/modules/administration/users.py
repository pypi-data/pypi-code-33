#!/usr/bin/env python3
"""
This module work with User class and access.

.create_new_user() - add new user to company.

.edit_user() - edit all user propertes.

.change_password() - change user password.

.try_to_enter_program() check user login/password.

.sync_user() - sync current user with database.

.show_all_users() - print all users from base.

.get_all_users_list() - get list of all users.
"""

import getpass
from typing import List
import bcrypt
from interkamen_career.modules.administration.logger_cfg import Logs
from interkamen_career.modules.support_modules.standart_functions import (
    BasicFunctionsS
    as BasF_S
)



LOGGER = Logs().give_logger(__name__)


class User(BasF_S):
    """User class."""

    __slots__ = (
        'name',
        'accesse',
        'login',
        'password',
        'email',
        'data_key',
        'temp_datakey'
    )

    def __init__(
            self,
            name,
            accesse,
            login,
            password,
            email,
            data_key,
            temp_datakey
    ):
        self.name = name
        self.accesse = accesse
        self.login = login
        self.password = password
        self.email = email
        self.data_key = data_key
        self.temp_datakey = temp_datakey

    def __repr__(self):
        output = (f"\nname:{self.name}\nlogin:{self.login}"
                  f"\naccesse:{self.accesse}"
                  f"\nemail:{self.email}")
        return output


class Users(BasF_S):
    """Users warking with program."""

    __slots__ = (
        'data_path',
        'user',
        'users_base',
    )

    access_list = ['admin', 'boss', 'master', 'mechanic', 'info']

    def __init__(self, user):
        self.user = user
        self.data_path = super().get_root_path() / 'data' / 'users_base'
        if not self.data_path.exists():
            self._create_new_users_base()
        self.users_base = super().load_data(
            data_path=self.data_path,
            decrypt=False,
        )

    def __repr__(self):
        output = ['']
        for login in self.users_base:
            for parametr in self.users_base[login]:
                output.append(
                    parametr + ':' + self.users_base[login][parametr])
            output.append('\n')
        return ' '.join(output)

    def _save_data_key(self, data_key):
        """Save data_key to file."""
        root_path = super().get_root_path() / 'secret_key'
        root_path.write_bytes(data_key)
        print(
            "'secret_key' file was created in:"
            f"\n{str(root_path)}"
            "\nSave it in safe place!"
            "\nIt'll be imposible to restore files if you miss it."
        )

    def _create_new_users_base(self):
        """Create new users base with new 'admin' account and key
        for encrypt database.
        """
        data_key = super().create_new_key()
        self._save_data_key(data_key)
        admin_user = self._fill_new_user(
            name='Main Program Admin',
            accesse='admin',
            login='admin',
            password='admin',
            data_key=data_key,
        )
        users_base = {'admin': admin_user}
        super().dump_data(
            data_path=self.data_path,
            base_to_dump=users_base,
            encrypt=False,
        )
        print(
            "\nDefault administration account created:"
            "\nlogin: admin"
            "\npassword: admin\n"
        )

    def _fill_new_user(self, name, accesse, login, password, data_key) -> User:
        """Fill new user."""
        password = password.encode('utf-8')
        coded_datakey = self._encode_datakey_with_pass(password, data_key)
        password = bcrypt.hashpw(password, bcrypt.gensalt())
        new_user = {
            'name': name,
            'accesse': accesse,
            'login': login,
            'password': password,
            'email': 'empty',
            'data_key': coded_datakey,
            'temp_datakey': None,
        }
        new_user = User(**new_user)
        return new_user

    def _encode_datakey_with_pass(self, password, datakey):
        """Encode datakey with user password."""
        password_to_key = super().make_key_length(password)
        coded_datakey = super().encrypt_data(password_to_key, datakey)
        return coded_datakey

    @classmethod
    @BasF_S.confirm_deletion_decorator
    def _check_deletion(cls, user: User):
        """Delete user from database"""
        if 'key' in user:
            print("Yoy can't delete main admin user.")
            check = False
        else:
            check = True
        return check, user.login

    def _delete_user(self, user: User):
        """delete user from database."""
        user_deleted = False
        deletion_approved = self._check_deletion(user)
        if deletion_approved:
            self.users_base.pop(user.login, None)
            super().dump_data(
                data_path=self.data_path,
                base_to_dump=self.users_base,
                encrypt=False,
            )
            user_deleted = True
            LOGGER.warning(
                f"User '{self.user.login}' delete user '{user.login}'")
        input('\n[ENTER] - выйти')
        return user_deleted

    def _change_user_access(self, user: User):
        """Change_user_access"""
        print("Choose new accesse:")
        new_accesse = super().choise_from_list(self.access_list)
        user.accesse = new_accesse
        LOGGER.warning(
            f"User '{self.user.login}' change access {user.login}")

    def _change_user_name(self, user: User):
        """Change user name"""
        new_name = input("Input new user name: ")
        old_name = user.name
        user.name = new_name
        LOGGER.warning(
            f"User '{self.user.login}' change name {old_name} -> {new_name}"
        )

    def _change_user_email(self, user: User):
        """Change user email"""
        new_email = super().check_correct_email()
        old_email = user.email
        user.email = new_email
        LOGGER.warning(
            f"User '{self.user.login}' change email {old_email} -> {new_email}"
        )

    def _working_with_user(self, choosen_user):
        """Edit choosen user."""
        while True:
            super().clear_screen()
            temp_user = self.users_base[choosen_user]
            print()
            print(self.users_base[choosen_user])
            edit_menu_dict = {
                'change user access': self._change_user_access,
                'change user name': self._change_user_name,
                'change user password': self.change_password,
                'delete user': self._delete_user,
                'change email': self._change_user_email,
                '[exit edition]': 'break',
            }
            print("Choose action:")
            choosen_action = super().choise_from_list(edit_menu_dict)

            print()
            if choosen_action in ['[exit edition]', '']:
                break
            are_user_deleted = edit_menu_dict[choosen_action](temp_user)
            if are_user_deleted:
                break
            self.users_base[choosen_user] = temp_user
            super().dump_data(
                data_path=self.data_path,
                base_to_dump=self.users_base,
                encrypt=False,
            )

    def _try_set_new_password(self, user):
        while True:
            new_password = getpass.getpass("Введите новый пароль: ")
            if not new_password:
                break
            repeat_password = getpass.getpass("Повторите новый пароль: ")
            if new_password == repeat_password:
                self._save_user_with_new_pass(user, new_password)
                print("Новый пароль сохранен.")
                LOGGER.warning(
                    f"User '{user.login}' change password")
                input('\n[ENTER] - продолжить.')
                return new_password
            else:
                print("Введенные пароли не совпадают.")
                input('\n[ENTER] - продолжить.')
            return new_password

    def _save_user_with_new_pass(self, user, new_password):
        """Save user with new password in users base."""
        new_password = new_password.encode('utf-8')
        user.data_key = self._encode_datakey_with_pass(
            new_password,
            user.temp_datakey
        )
        save_data_key = user.temp_datakey
        # We must save in base without decrypted data key.
        user.temp_datakey = None
        user.password = bcrypt.hashpw(new_password, bcrypt.gensalt())
        self.users_base[user.login] = user
        super().dump_data(
            data_path=self.data_path,
            base_to_dump=self.users_base,
            encrypt=False,
        )
        # Return data key to current user.
        user.temp_datakey = save_data_key

    def create_new_user(self):
        """Create new user and save him in databese"""
        new_user = {}
        new_user['name'] = input("Input username: ")
        while True:
            new_user['login'] = input("Input login: ")
            if new_user['login'] in self.users_base:
                print("Login alredy exist, try enother.")
            elif not new_user['login']:
                print("You must input login.")
            else:
                break
        new_user['password'] = input("Input password: ")
        print("Choose access by number:")
        new_user['accesse'] = super().choise_from_list(self.access_list)
        new_user['data_key'] = self.user.temp_datakey
        new_user = self._fill_new_user(**new_user)
        self.users_base[new_user.login] = new_user
        print(f"\033[92m user '{new_user.login}' created. \033[0m")
        LOGGER.warning(
            f"User '{self.user.login}' create new user: '{new_user.login}'")
        super().dump_data(
            data_path=self.data_path,
            base_to_dump=self.users_base,
            encrypt=False,
        )
        input('\n[ENTER] - выйти')

    def edit_user(self):
        """Change user parametrs."""
        while True:
            super().clear_screen()
            print("Input number of user to edit:")
            choosen_user = super().choise_from_list(
                self.users_base, none_option=True)
            if choosen_user:
                self._working_with_user(choosen_user)
            else:
                break

    def change_password(self, user):
        """Changing password."""
        while True:
            old_password = input("Введите старый пароль: ")
            old_password = old_password.encode('utf-8')
            if bcrypt.checkpw(old_password, user.password):
                new_password = self._try_set_new_password(user)
                if new_password:
                    break
            elif not old_password:
                break
            else:
                print("Неправильный пароль.")
                input('\n[ENTER] - продолжить.')

    def try_to_enter_program(self):
        """Take user login/password input and return current user privilege.
        """
        user_in = None
        while True:
            login = input("Имя пользователя: ")
            password = getpass.getpass("Введите пароль: ")
            password = password.encode('utf-8')
            sucsesse_login = super().check_login_password(
                self.users_base,
                login,
                password
            )
            if sucsesse_login:
                key = super().make_key_length(password)
                user_in = self.users_base[login]
                user_in.temp_datakey = super().decrypt_data(
                    key,
                    user_in.data_key
                )
                break
        return user_in

    def show_all_users(self):
        """Print all users from base"""
        for login in self.users_base:
            print(self.users_base[login])
        input('\n[ENTER] - выйти')

    def get_all_users_list(self) -> List['Users']:
        """Get all users list"""
        users_list = [user for user in self.users_base]
        return users_list

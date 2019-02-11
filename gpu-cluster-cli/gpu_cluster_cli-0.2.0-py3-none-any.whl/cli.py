import click
import requests
import json
import getpass
import pickle
import os
import sys
import re
import pkg_resources
from threading import Thread
from executor import execute
from terminaltables import SingleTable
from pyfiglet import Figlet

from cli import config

HOST = "http://" + config.HOST['host'] + ":" + str(config.HOST['port'])
COOKIEPATH = os.path.join(os.path.expanduser('~'), 'gpu_cli_cookie.txt')

class MyException(Exception):
    pass

class LoginException(Exception):
    def __init__(self):
        super().__init__("Failed to get session info. Please log in.")

class PermissionException(Exception):
    def __init__(self):
        super().__init__("You have no permission.")

class ConnectionException(Exception):
    def __init__(self):
        super().__init__("Unable to connect API server.")

class InternalErrorException(Exception):
    def __init__(self):
        super().__init__("Server internal error occurred. Ask to operator.")

class OtherException(Exception):
    def __init__(self, code, message):
        super().__init__("{}: {}".format(code, message))


def response_parser(response):
    if response.ok:
        return json.loads(response.content)
    elif response.status_code == 401:
        raise LoginException
    elif response.status_code == 403:
        raise PermissionException
    elif response.status_code == 500:
        raise InternalErrorException
    else:
        raise OtherException(response.status_code, response.reason)


def save_cookie(session):
    with open(COOKIEPATH, 'wb') as f:
        pickle.dump(session.cookies, f)


def load_cookie(session):
    with open(COOKIEPATH, 'rb') as f:
        session.cookies.update(pickle.load(f))


def check_version():
    res = requests.get(url=HOST+"/auth/checkversion")
    req_version = response_parser(res)

    curr_version = pkg_resources.require('gpu-cluster-cli')[0].version
    parsed_curr_version = list(map(int, curr_version.split(".")))
    parsed_req_version = list(map(int, req_version['version'].split(".")))

    if parsed_curr_version < parsed_req_version:
        print("You should upgrade santa to version {}".format(req_version))
        sys.exit()


def check_login(session):
    try:
        load_cookie(session)
    except:
        raise LoginException

    res = session.get(url=HOST+"/auth/checksession")
    username = response_parser(res)['user']
    
    if username is None:
        raise LoginException

    print("User: {}".format(username))
    return username


def check_level(session):
    try:
        load_cookie(session)
    except:
        raise LoginException

    res = session.get(url=HOST+"/auth/checklevel")
    userlevel = response_parser(res)['level']

    if userlevel is None:
        raise LoginException

    return userlevel


def get_images(session, custom=False):
    try:
        load_cookie(session)
    except:
        raise LoginException

    res = session.get(url=HOST+"/container/images")
    imagelist = response_parser(res)['images']

    image_data = [["#", "Repository", "Tag"]]

    for i, img in enumerate(imagelist):
        image_data.append((i + 1, img['repository'], img['tag']))

    if custom:
        image_data.append((len(imagelist) + 1, "Other", ""))

    image_table = SingleTable(image_data)
    image_table.inner_row_border = True
    print("### Images")
    print(image_table.table)

    return imagelist


def showlogo():
    version = pkg_resources.require("gpu-cluster-cli")[0].version
    f = Figlet(font='banner3-D')
    print(f.renderText('SANTA'))
    print("v. {}".format(version))


def translate(message):
    message = message.replace("pod", "container")
    message = message.replace("Pod", "Container")
    message = message.replace("POD", "CONTAINER")
    return message


@click.group()
def cli():
    if os.name == "nt" and "437" not in os.popen("chcp").read():
        res = os.popen("chcp 437").read()

        if res != "Active code page: 437\n":
            print("Warning: showing tables could have problems.")

    check_version()


@cli.command()
def register():
    showlogo()

    username = None
    password = None
    password_re = None

    print('-' * 19, '  Register  ', '-' * 19)
    print()

    username_checker = re.compile(r'^(([A-Za-z0-9][-A-Za-z0-9_.]*)?[A-Za-z0-9])$')

    while True:
        username = input('Input username: ')

        if username_checker.match(username):
            if username == "unknown":
                print("Username 'unknown' is prohibited.")
            else:
                break
        else:
            print("Username must consist of alphanumeric characters, '-', '_' or '.'.")
            print("And must start and end with an alphanumeric character.")
            print("ex) 'MyValue',  or 'my_value',  or '12345'")
            print()  
            
    while not password:
        password = getpass.getpass('Input password: ')

    while not password_re:
        password_re = getpass.getpass('Input password again: ')

    phone_checker = re.compile(r'^(?:(010\d{4})|(01[1|6|7|8|9]\d{3,4}))(\d{4})$')
    phone_checker_with_dash = re.compile(r'^(?:(010-\d{4})|(01[1|6|7|8|9]-\d{3,4}))-(\d{4})$')

    while True:
        phone = input('Input phone number: ')

        if phone_checker.match(phone):
            phone = phone[:3] + '-' + phone[3:-4] + '-' + phone[-4:]
            break
        elif phone_checker_with_dash.match(phone):
            break
        else:
            print("Invalid phone number.")

    email_checker = re.compile(r'^[a-zA-Z0-9_.+-]+@(?:(?:[a-zA-Z0-9-]+\.)?[a-zA-Z]+\.)?lgcns\.com$')

    while True:
        email = input('Input email address with @lgcns.com: ')

        if email_checker.match(email):
            break
        else:
            print("Invalid email address.")

    print()
    print('-' * 52)

    if password != password_re:
        print("Passwords does not match.")
    else:
        res = requests.post(
            url=HOST+"/auth/register",
            data={
                'username': username,
                'password': password,
                'phone': phone,
                'email': email
            })
        parsed_result = response_parser(res)

        if parsed_result is not None:
            print(parsed_result['message'])


@cli.command()
def login():
    showlogo()

    sess = requests.session()

    username = None
    password = None

    print('-' * 20, '  Login  ', '-' * 21)
    print()

    while not username:
        username = input('Input username: ')

    while not password:
        password = getpass.getpass('Input password: ')

    print()
    print('-' * 52)

    res = sess.post(
        url=HOST+"/auth/login",
        data={
            'username': username,
            'password': password
        })
    parsed_result = response_parser(res)

    if parsed_result is not None:
        print(parsed_result['message'])

    save_cookie(sess)


@cli.command()
def logout():
    sess = requests.session()
    username = check_login(sess)

    sess.get(url=HOST+"/auth/logout")
    os.remove(COOKIEPATH)
    if os.name == "nt":
        os.system("chcp 949")

    print('User {} has logged out.'.format(username))
    print('-' * 52)


@cli.command()
def changepw():
    sess = requests.session()
    username = check_login(sess)

    curr_password = None
    new_password = None
    new_password_re = None

    print('-' * 15, '  Change password  ', '-' * 16)
    print()

    while not curr_password:
        curr_password = getpass.getpass('Input current password: ')

    while not new_password:
        new_password = getpass.getpass('Input new password: ')

    while not new_password_re:
        new_password_re = getpass.getpass('Input new password again: ')

    print()
    print('-' * 52)

    if new_password != new_password_re:
        print('New passwords does not match.')
    else:
        res = sess.post(
            url=HOST+"/auth/changepw",
            data={
                'curr_password': curr_password,
                'new_password': new_password
            })
        parsed_result = response_parser(res)

        if parsed_result is not None:
            print(parsed_result['message'])


@cli.command()
def users():
    sess = requests.session()
    username = check_login(sess)
    userlevel = check_level(sess)

    if userlevel == 'admin':
        print('-' * 19, '  User List  ', '-' * 20)
        print()

        res = sess.get(url=HOST+"/auth/userlist")
        parsed_result = response_parser(res)

        if parsed_result is not None:
            user_data = [['#', 'username', 'usertype', 'phone', 'email']]
            for i, user in enumerate(parsed_result['users']):
                user_row = [i + 1]
                user_row.extend(user)
                user_data.append(user_row)
            user_table = SingleTable(user_data)
            user_table.inner_row_border = True
            print("### Users")
            print(user_table.table)
            print()

    else:
        raise PermissionException


@cli.command()
def changelevel():
    sess = requests.session()
    username = check_login(sess)
    userlevel = check_level(sess)

    if userlevel == 'admin':
        target_username = None
        target_userlevel = None

        print('-' * 14, '  Change user level  ', '-' * 15)
        print()

        info_res = sess.get(url=HOST+"/auth/userlist")
        parsed_info = response_parser(info_res)

        if parsed_info is not None:
            user_data = [['#', 'username', 'usertype', 'phone', 'email']]
            userinfo = parsed_info['users']
            users = []

            for i, user in enumerate(userinfo):
                user_row = [i + 1]
                user_row.extend(user)
                user_data.append(user_row)
                users.append(user[0])
            user_table = SingleTable(user_data)
            user_table.inner_row_border = True
            print("### Users")
            print(user_table.table)

            while True:
                target_username = input('Input username to change: ')

                if target_username in users:
                    break
                else:
                    print("User [{}] does not exist.".format(target_username))

            while True:
                target_userlevel = input(
                    'Input new user level for [{}] (admin, superuser, normal): '.format(target_username))

                if target_userlevel in ["admin", "superuser", "normal"]:
                    break
                else:
                    print("Invalid user level.")

            print()
            print('-' * 52)

            change_res = sess.post(
                url=HOST+"/auth/changetype",
                data={
                    'username': target_username,
                    'usertype': target_userlevel
                })
            parsed_change = response_parser(change_res)

            if parsed_change is not None:
                print(parsed_change['message'])

    else:
        raise PermissionException


@cli.command()
def deleteuser():
    sess = requests.session()
    username = check_login(sess)
    userlevel = check_level(sess)

    if userlevel == 'admin':
        target_username = None

        print('-' * 14, '  Change user level  ', '-' * 15)
        print()

        info_res = sess.get(url=HOST+"/auth/userlist")
        parsed_info = response_parser(info_res)

        if parsed_info is not None:
            user_data = [['#', 'username', 'usertype', 'phone', 'email']]
            userinfo = parsed_info['users']
            users = []

            for i, user in enumerate(userinfo):
                user_row = [i + 1]
                user_row.extend(user)
                user_data.append(user_row)
                users.append(user[0])
            user_table = SingleTable(user_data)
            user_table.inner_row_border = True
            print("### Users")
            print(user_table.table)

        while True:
            target_username = input('Input username to delete: ')

            if target_username in users:
                break
            else:
                print("User [{}] does not exist.".format(target_username))

        check = input('Proceed to delete user [{}]? (yes/no): '.format(target_username))

        print()
        print('-' * 52)

        if check.lower() == "yes":
            res = sess.post(
                url=HOST+"/auth/deleteuser",
                data={
                    'username': target_username,
                })
            parsed_result = response_parser(res)

            if parsed_result is not None:
                print(parsed_result['message'])

    else:
        raise PermissionException


@cli.command()
def images():
    sess = requests.session()
    username = check_login(sess)

    print('-' * 20, '  Images  ', '-' * 20)
    print()

    get_images(sess)


@cli.command()
def getinfo():
    sess = requests.session()
    username = check_login(sess)

    print('-' * 13, '  GPU, container Info  ', '-' * 14)
    print()

    res = sess.get(url=HOST+"/container/getinfo")
    parsed_result = response_parser(res)

    if parsed_result is not None:
        if parsed_result['status'] == 'Success':
            pod_data = [['#', 'user', 'container_name', 'container_id', 'ports', 'GPUs', 'Status']]
            for i, pod in enumerate(parsed_result['pods']):
                pod_row = [i + 1]
                pod_row.extend(pod)
                pod_data.append(pod_row)
            pod_table = SingleTable(pod_data)
            pod_table.inner_row_border = True
            print("###", parsed_result['message'])
            print(pod_table.table)
            print()

            user_data = [['user', 'GPUs']]
            for k in parsed_result['userGPUs'].keys():
                user_data.append([k, parsed_result['userGPUs'][k]])
            user_table = SingleTable(user_data)
            print("### GPU usage per user")
            print(user_table.table)
            print()

            gpu_data = [
                ['In use', 'Total GPUs'],
                [parsed_result['using'], parsed_result['total']]
            ]
            gpu_table = SingleTable(gpu_data)
            print("### GPU status")
            print(gpu_table.table)

        else:
            print(translate(parsed_result['message']))


@cli.command()
def getgpu():
    sess = requests.session()
    username = check_login(sess)

    min_gpu = config.GPU['min']
    max_gpu = config.GPU['max']

    print('-' * 19, '  Get GPU  ', '-' * 20)
    print()

    info_res = sess.get(url=HOST+"/container/getinfo")
    parsed_info = response_parser(info_res)

    if parsed_info is not None:
        if parsed_info['status'] == 'Success':
            gpu_data = [
                ["In use", "Total GPUs"],
                [parsed_info['using'], parsed_info['total']]
            ]
            gpu_table = SingleTable(gpu_data)
            print("### GPU status")
            print(gpu_table.table)

            gpu_limit = min(max_gpu, parsed_info['total'] - parsed_info['using'])

            while True:
                try:
                    num_gpu = int(input('Input number of GPUs you need ({} ~ {}): '.format(min_gpu, gpu_limit)))

                    if num_gpu < min_gpu:
                        raise ValueError
                    elif num_gpu > gpu_limit:
                        print("Insufficient GPUs.\n")
                    else:
                        print()
                        break
                except ValueError:
                    print("Invalid input.\n")

            imagelist = get_images(sess, custom=True)
            num_images = len(imagelist) + 1

            while True:
                try:
                    image_idx = int(input('Select docker image (1 ~ {}): '.format(num_images)))

                    if image_idx < 1 or image_idx > num_images:
                        raise ValueError
                    elif image_idx == num_images:
                        while True:
                            image = input('Input image in repository:tag format. ex) ubuntu:18.04 : ')

                            if image:
                                break
                        break
                    else:
                        image = "{}:{}".format(
                            imagelist[image_idx - 1]['repository'],
                            imagelist[image_idx - 1]['tag'])
                        print()
                        break
                except ValueError:
                    print("Invalid input.\n")

            pod_name_checker = re.compile(r'^(([A-Za-z0-9][-A-Za-z0-9_.]*)?[A-Za-z0-9])$')

            while True:
                pod_name = input('Input container name: ')

                if pod_name_checker.match(pod_name):
                    break
                else:
                    print("Container name must consist of alphanumeric characters, '-', '_' or '.'.")
                    print("And must start and end with an alphanumeric character.")
                    print("ex) 'MyValue',  or 'my_value',  or '12345'")
                    print()

            while True:
                ports_str = input((
                            "\nInput ports to use.\n"
                            "  SSH port 22 will be given in default.\n"
                            "  Ports should be between [1024 ~ 49151].\n"
                            "  Seperate ports by comma.\n"
                            "  ex) 6006,8888\n"
                            "ports: "))

                if ports_str:
                    try:
                        ports = set(map(int, ports_str.split(",")))

                        for port in ports:
                            if port < 1024 or port > 49151:
                                raise MyException

                        ports_param = ",".join(str(p) for p in ports)
                        print()
                        break

                    except (ValueError, MyException):
                        print("Invalid port.")

                else:
                    ports_param = None
                    break

            create_res = sess.post(
                url=HOST+"/container/getgpu",
                data={
                    'pod_name': pod_name,
                    'image': image,
                    'num_gpu': num_gpu,
                    'ports': ports_param
                    })

            parsed_create = response_parser(create_res)

            if parsed_create is not None:
                print(translate(parsed_create['message']))
        else:
            print(translate(parsed_info['mesaage']))
        

@cli.command()
def returngpu():
    sess = requests.session()
    username = check_login(sess)

    print('-' * 18, '  Return GPU  ', '-' * 18)
    print()

    info_res = sess.get(url=HOST+"/container/getinfo")
    parsed_info = response_parser(info_res)

    if parsed_info is not None:
        if parsed_info['status'] == 'Success':
            pod_list = parsed_info['pods']

            pod_data = [['#', 'user', 'container_name', 'container_id', 'ports', 'GPUs', 'Status']]
            for i, pod in enumerate(pod_list):
                pod_row = [i + 1]
                pod_row.extend(pod)
                pod_data.append(pod_row)
            pod_table = SingleTable(pod_data)
            pod_table.inner_row_border = True
            print("###", parsed_info['message'])
            print(pod_table.table)

            if pod_list:
                while True:
                    try:
                        pod_index = int(input("Select container (1~{}): ".format(len(pod_list))))

                        if pod_index < 1 or pod_index > len(pod_list):
                            raise MyException

                        pod_id = pod_list[pod_index-1][2]
                        break

                    except (ValueError, MyException):
                        print("Invalid input.\n")

                check = input('Proceed to delete container [{}]? (yes/no): '.format(pod_list[pod_index-1][1]))

                if check.lower() == "yes":
                    delete_res = sess.get(
                        url=HOST+"/container/returngpu",
                        data={'pod_id': pod_id})

                    parsed_delete = response_parser(delete_res)
                    print(translate(parsed_delete['message']))

            else:
                print("No container to return.")

        else:
            print(translate(parsed_info['message']))


def main():
    try:
        cli()
    except (LoginException, PermissionException, ConnectionException, InternalErrorException, OtherException) as e:
        print(e)
        sys.exit()
    except requests.exceptions.ConnectionError:
        print("Unable to connect API server.")
        sys.exit()

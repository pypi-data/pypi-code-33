import json
import os
import re
import requests


class E4Connect:
    """
    Class that allows to interact with the E4 Connect platform. It allows to retrieve lists of sessions and devices and
    to download sessions data.

    :param user: Username to log in the E4 Connect platform.
    :param pwd: Password to log in the E4 Connect platform.
    """

    _URL_AUTH = 'https://www.empatica.com/connect/authenticate.php'
    _URL_SESSIONS_MAIN = 'https://www.empatica.com/connect/sessions.php'
    _URL_SESSIONS_LIST = 'https://www.empatica.com/connect/connect.php/users/{uid}/sessions?from=0&to=999999999999'
    _URL_SESSION_DELETE = 'https://www.empatica.com/connect/connect.php/sessions/{id}'
    _URL_SESSION_DOWNLOAD = 'https://www.empatica.com/connect/download.php?id={id}'
    _URL_PURCHASED_DEVS = 'https://www.empatica.com/connect/connect.php/users/{uid}/api/purchasedDevices'

    def __init__(self, user: str = None, pwd: str = None):
        self.s = requests.Session()
        self.user_id = None

        if user and pwd:
            self.auth(user, pwd)

    def auth(self, user: str, pwd: str):
        """
        Allows to login in the platform and retrieves the related user ID. Cookies will be saved for later requests.
        
        :param user: Username to log in the E4 Connect platform.
        :param pwd: Password to log in the E4 Connect platform.
        """
        auth_info = {'username': user, 'password': pwd}
        self.s.post(E4Connect._URL_AUTH, auth_info).raise_for_status()

        resp = self.s.get(E4Connect._URL_SESSIONS_MAIN)
        resp.raise_for_status()
        self.user_id = re.search(r'userId = ([0-9]*);', resp.text).group(1)

    def sessions_list(self) -> list:
        """
        Retrieves a list of all the sessions in the current session. It includes the following columns: id, device_id,
        duration, status, start_time, label device, exit_code.

        :return: list of dictionaries with information of the sessions.
        """
        resp = self.s.get(E4Connect._URL_SESSIONS_LIST.format(uid=self.user_id))
        resp.raise_for_status()
        return json.loads(resp.text)

    def download_session(self, session_id: str, file_path: str = '.'):
        """
        Download all the data related with a specific session as a ZIP file. It includes the following parameters
        (separated in different files): ACC, BVP, EDA, HR, IBI and TEMP. It also includes a info.txt file explaining
        the data format and a tags.txt file specifying the events present in the data.

        :param session_id: numeric ID that identifies the session.
        :param file_path: path of the resulting output file.
        """
        resp = self.s.get(E4Connect._URL_SESSION_DOWNLOAD.format(id=session_id))
        file_path = os.path.join(file_path, '%s.zip' % session_id) if os.path.isdir(file_path) else file_path
        with open('%s' % file_path, 'wb') as f:
            f.write(resp.content)

    def remove_session(self, session_id: str):
        """
        Removes a session.

        :param session_id: numeric ID that identifies the session.
        """
        resp = self.s.delete(E4Connect._URL_SESSION_DELETE.format(id=session_id))
        resp.raise_for_status()

    def purchased_devices(self) -> list:
        """
        Retrieves a list of all the devices linked with the current session. It includes the following columns:
        device_id, label, model, hardware_code, purchase_code, purchase_id.

        :return: list of dictionaries with information of the devices.
        """
        resp = self.s.get(E4Connect._URL_PURCHASED_DEVS.format(uid=self.user_id))
        resp.raise_for_status()
        return json.loads(resp.text)

    def user_id(self) -> str:
        """
        Retrieves the numeric identifier of the user.

        :return: user ID.
        """
        return self.user_id


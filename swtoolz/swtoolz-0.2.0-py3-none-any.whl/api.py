from typing import Dict, List

import requests

# TODO: Добавить в Readme чейнджлог

class SWToolz:
    """
    Класс для удобного получения данных и управления оборудованием через сервис SWToolz-Core_.

    Пример использования::

        swt = SWToolz(swtoolz_url, swtoolz_user, swtoolz_community_number, swtoolz_port)
        swt.change_port_admin_state(device_ip, port_num, 'enabled')

    .. _SWToolz-Core: https://github.com/MXMP/swtoolz-core
    """

    def __init__(self, url: str, user: str, community_number: int, port: int = 7377, timeout: float = 2.0):
        """
        Начальная инициализация - установка основных полей, формирование шаблона URL для выполнения запросов.

        :param str url: url сервиса SWToolz-Core
        :param str user: логин пользователя в сервисе
        :param int community_number: номер комьюнити для выполнения команд
        :param int port: порт, на котором слушает сервис (по-умолчанию 7377)
        :param float timeout: таймаут для выполнения всех операций
        """

        self.server_url = url
        self.user = user
        self.community_number = community_number
        self.service_port = port
        self.timeout = timeout

        # Т.к. SWToolz-Core принимает параметры запроса не как GET-параметры, а парсит URL, то для удобства
        # использования используем шаблон для формирования конечного URL, куда впоследствии будут подставляться
        # ip-адрес устройства и команда.
        self.request_url_template = f'{self.server_url}:{self.service_port}/{self.user}/{{device_ip}}/' \
            f'{self.community_number}/{{command}}'

    @staticmethod
    def reverse_dict(input_dict: Dict) -> Dict:
        """
        Меняет местами ключи и значения.

        :param Dict input_dict: словарь, в котором нужно менять местами ключи со значениями
        :rtype Dict:
        :return: словарь, в котором поменяны местами ключи со значениями
        """
        output_dict = {}
        for key, value in input_dict.items():
            output_dict[value] = key

        return output_dict

    def make_request_url(self, device_ip: str, commands: List) -> str:
        """
        Формирует строку для выполонения запроса к SWToolz-Core, команды "склеиваются" через '+/'.

        :param str device_ip: ip-адрес коммутатора
        :param List commands: список с командами
        :rtype str:
        :return: url для выполнения запроса
        """

        # если команды переданы как строка, то формируем из них список из одного элемента
        if isinstance(commands, str):
            commands = [commands]

        return self.request_url_template.format(device_ip=device_ip, command='+/'.join(commands))

    def execute(self, device_ip: str, commands: List) -> Dict:
        """
        Выполняем запрос к SWToolz-Core, предварительно "склеив" команды.

        :param str device_ip: ip-адрес коммутатора
        :param List commands: список с командами (если на входе строка, то она приведется к списку)
        :rtype Dict:
        :return: словарь с результатами запроса
        """

        url = self.make_request_url(device_ip, commands)
        response = requests.get(url, timeout=self.timeout)

        if response.status_code == requests.codes.ok:
            return response.json()['response']['data']
        else:
            # TODO: кидать эксепшн наверное лучше будет
            return False

    def get_dict(self, device_ip: str, dict_name: str, reverse: bool = False) -> Dict:
        """
        Возвращает запрашиваемый словарь соответствия (если reverse установлен в True, то ключи и значения в
        словаре меняются местами).

        :param str device_ip: ip-адрес коммутатора
        :param str dict_name: название словаря для получения
        :param bool reverse: менять ли местами ключи и значения в словаре
        :rtype Dict:
        :return: словарь соответсвия
        """

        result_dict = self.execute(device_ip, [dict_name])[dict_name]
        return self.reverse_dict(result_dict) if reverse else result_dict

    def get_admin_status_dict(self, device_ip: str, reverse: bool = False) -> Dict:
        """
        Возвращает словарь "административное состояние -> код" (если reverse установлен в True, то ключи и значения в
        словаре меняются местами).

        :param str device_ip: ip-адрес коммутатора
        :param bool reverse: менять ли местами ключи и значения в словаре
        :rtype Dict:
        :return: словарь соответсвия
        """

        if reverse:
            return self.get_dict(device_ip, 'AdminStatus', True)
        else:
            return self.get_dict(device_ip, 'AdminStatus')

    def get_medium_type_dict(self, device_ip: str, reverse: bool = False) -> Dict:
        """
        Возвращает словарь "тип среды -> код" (если reverse установлен в True, то ключи и значения в
        словаре меняются местами).

        :param str device_ip: ip-адрес коммутатора
        :param bool reverse: менять ли местами ключи и значения в словаре
        :rtype Dict:
        :return: словарь соответсвия
        """

        if reverse:
            return self.get_dict(device_ip, 'MediumType', True)
        else:
            return self.get_dict(device_ip, 'MediumType')

    def get_device_map(self, device_ip: str) -> List:
        """
        Возвращает "карту портов" для устройства.

        :param str device_ip: ip-адрес коммутатора
        :rtype List:
        :return: карта портов в виде списка слотов
        """

        return self.execute(device_ip, ['DeviceMap'])['DeviceMap']

    def get_stack_info(self, device_ip: str) -> Dict:
        """
        Возвращает словарь "StackInfo".

        :param str device_ip: ip-адрес коммутатора
        :rtype: Dict
        :return: словарь "StackInfo"
        """

        return self.get_dict(device_ip, 'StackInfo')

    def get_commands(self, device_ip: str) -> List:
        """
        Возвращает список рекомендуемых команд для данного устройства.

        :param str device_ip: ip-адрес коммутатора
        :rtype: List
        :return: список рекомендуемых комманд
        """

        return self.execute(device_ip, ['Commands'])['Commands']

    def get_actual_status_dict(self, device_ip: str) -> Dict:
        """
        Возвращает словарь сопоставления статуса порта (линк есть или нет).

        :param str device_ip: ip-адрес коммутатора
        :rtype: Dict
        :return: словарь ActualStatus
        """

        return self.get_dict(device_ip, 'ActualStatus')

    def get_actual_speed_dict(self, device_ip: str) -> Dict:
        """
        Возвращает словарь сопоставления скоростей для порта.

        :param str device_ip: ip-адрес коммутатора
        :rtype: Dict
        :return: словать ActualSpeed
        """

        return self.get_dict(device_ip, 'ActualSpeed')

    # TODO: сделать какой-то wrapper для запросов к SWToolz-Core, что бы нормально распозновать ошибки
    def change_port_admin_state(self, device_ip: str, port_num: int, target_state: str) -> bool:
        """
        Изменяет административное состояние порта, т.е. включает его или выключает в зависимости от переданного
        `target_state`.

        :param str device_ip: ip-адрес коммутатора
        :param int port_num: номер порта коммутатора
        :param str target_state: целевое состояние порта включен/выключен (принимает строки 'enabled' и 'disabled')
        :rtype: bool
        :return: успешность выполнения команды
        """

        # К сожалению, API SWToolz-Core не очень удобен. Поэтому чтобы понять какой числовой код нужно слать сервису
        # чтобы включить или выключить порт нужно сначала спросить "словарь соответствия" AdminStatus. Сделано это так,
        # потому что на всех устройствах разные SNMP индексы для состояний.
        admin_status_dict = self.get_admin_status_dict(device_ip=device_ip, reverse=True)

        # Для того, что бы включить/выключить порт нужно послать SWToolz-Core команду
        # set_AdminStatus/{номер порта}/{код нужного административного состояния}
        try:
            command_url_part = f'set_AdminStatus/{port_num}/{admin_status_dict[target_state]}'
        except KeyError:
            # неправильно передан target_state
            return False
        # подставляем в шаблон URL команду и ip-адрес устройства
        change_state_url = self.make_request_url(device_ip, [command_url_part])
        change_state_response = requests.get(change_state_url, timeout=self.timeout)
        if change_state_response.status_code == requests.codes.ok:
            # проверяем выполнилась ли команда
            # такое может произойти если, например, неправильно указан индекс SNMP community, ответ придет с нормальным
            # HTTP-кодом, а команда выполнена не будет
            if change_state_response.json()['response']['data']['set_AdminStatus'] == 1:
                return True

        return False

    def get_port_admin_state(self, device_ip: str, port_num: int, media: str = 'copper') -> str:
        """
        Возвращает административное состояние порта.

        :param str device_ip: ip-адрес коммутатора
        :param int port_num: номер порта коммутатора
        :param str media: тип среды ('copper'/'fiber'), по-умолчанию - "медь"
        :rtype str:
        :return: административное состояние ('enabled'/'disabled')
        """

        # К сожалению, API SWToolz-Core не очень удобен. Поэтому чтобы понять какой числовой код какому типу среды или
        # административному состоянию соответствует, нужно сначала спросить "словари соответствия" AdminStatus и
        # MediumType. Сделано это так, потому что на всех устройствах разные SNMP индексы для состояний.
        admin_status_dict = self.get_admin_status_dict(device_ip)
        medium_type_dict = self.get_medium_type_dict(device_ip, True)

        # Для того, что бы узнасть администартивное состояние порта нужно послать SWToolz-Core команду
        # get_SinglePort/{номер порта}, тем самым узнав всю информацию об этом порту. А потом уже оттуда выбрать, то
        # что нужно.
        admin_status = self.execute(device_ip, [f'get_SinglePort/{port_num}'])
        try:
            status_code = admin_status['AdminStatus'][f'{port_num}.{medium_type_dict[media]}']
            return admin_status_dict[status_code]
        except IndexError:
            return ''

    def get_port_actual_status(self, device_ip: str, port_num: int, media: str = 'copper') -> str:
        """
        Возвращает актуальное состояние порта 'linkup'/'linkdown'.

        :param str device_ip: ip-адрес коммутатора
        :param int port_num: номер порта коммутатора
        :param str media: тип среды ('copper'/'fiber'), по-умолчанию - "медь"
        :rtype str:
        :return: актуальное состояние ('linkup'/'linkdown')
        """

        # К сожалению, API SWToolz-Core не очень удобен. Поэтому чтобы понять какой числовой код какому типу среды или
        # актуальному состоянию соответствует, нужно сначала спросить "словари соответствия" ActualStatus и
        # MediumType. Сделано это так, потому что на всех устройствах разные SNMP индексы для состояний.
        actual_status_dict = self.get_dict(device_ip, 'ActualStatus')
        medium_type_dict = self.get_medium_type_dict(device_ip, True)

        # Для того, что бы узнасть актуальное состояние порта нужно послать SWToolz-Core команду
        # get_SinglePort/{номер порта}, тем самым узнав всю информацию об этом порту. А потом уже оттуда выбрать, то
        # что нужно.
        actual_status = self.execute(device_ip, [f'get_SinglePort/{port_num}'])
        try:
            status_code = actual_status['ActualStatus'][f'{port_num}.{medium_type_dict[media]}']
            return actual_status_dict[status_code]
        except IndexError:
            return ''

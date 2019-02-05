import re
import subprocess

from pyhap.accessory import Accessory
from pyhap.const import CATEGORY_SWITCH

PLIST_RE = re.compile(r'^"(?P<key>.*?)" = <?"?(?P<value>.*?)"?>?$')


def get_display_state():
    result = subprocess.check_output(['pmset', '-g', 'powerstate', 'IODisplayWrangler'])
    return int(result.strip().split(b'\n')[-1].split()[1]) >= 4


def set_display_state(state):
    if state:
        subprocess.call(['caffeinate', '-u', '-t', '1'])
    else:
        subprocess.call(['pmset', 'displaysleepnow'])


def get_machine_info():
    result = [
        x.strip().decode()
        for x in subprocess.check_output(['ioreg', '-c', 'IOPlatformExpertDevice', '-d', '2']).split(b'\n')
    ]
    result = result[result.index('{') + 1:result.index('}')]

    data = {
        key: value
        for key, value in [
            PLIST_RE.match(row).groups()
            for row in result
            if PLIST_RE.match(row)
        ]
    }

    return {
        'SerialNumber': data['IOPlatformSerialNumber'],
        'Model': data['model'],
        'Manufacturer': data['manufacturer'],
    }


class DisplaySwitch(Accessory):
    category = CATEGORY_SWITCH

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.display = self.add_preload_service('Switch').configure_char(
            'On', setter_callback=self.set_display
        )

    def add_info_service(self):
        info_service = self.driver.loader.get_service('AccessoryInformation')
        info_service.configure_char('Name', value=self.display_name)
        for name, value in get_machine_info().items():
            info_service.configure_char(name, value=value)
        self.add_service(info_service)

    @Accessory.run_at_interval(1)
    def run(self):
        state = get_display_state()

        if self.display.value != state:
            self.display.value = state
            self.display.notify()

    def set_display(self, state):
        if get_display_state() != state:
            set_display_state(state)

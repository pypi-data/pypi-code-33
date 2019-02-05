import random
import signal
import subprocess
from pathlib import Path

from pyhap.accessory_driver import AccessoryDriver

from .display_switch import DisplaySwitch

path = Path(__file__).parent / 'display-switch.state'


def main():
    driver = AccessoryDriver(
        port=random.randint(50000, 60000),
        persist_file=path.resolve(),
    )
    driver.add_accessory(accessory=DisplaySwitch(
        driver,
        subprocess.check_output(['hostname', '-s']).strip().decode(),
    ))

    signal.signal(signal.SIGTERM, driver.signal_handler)
    driver.start()

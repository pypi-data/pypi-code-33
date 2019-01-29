from setuptools import setup, find_packages

setup(
    name="iotile_support_con_nrf52832_3",
    packages=find_packages(include=["iotile_support_con_nrf52832_3.*", "iotile_support_con_nrf52832_3"]),
    version="3.2.0rc1",
    install_requires=['iotile_support_lib_controller_3 >= 3.7.13, == 3.*'],
    entry_points={'iotile.proxy': ['nrf52832_controller = iotile_support_con_nrf52832_3.nrf52832_controller']},
    author="Arch",
    author_email="info@arch-iot.com"
)
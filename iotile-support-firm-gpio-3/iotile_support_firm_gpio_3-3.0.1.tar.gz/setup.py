from setuptools import setup, find_packages

setup(
    name="iotile_support_firm_gpio_3",
    packages=find_packages(include=["iotile_support_firm_gpio_3.*", "iotile_support_firm_gpio_3"]),
    version="3.0.1",
    install_requires=[],
    entry_points={'iotile.proxy': ['gpio1_proxy = iotile_support_firm_gpio_3.gpio1_proxy']},
    author="Arch",
    author_email="info@arch-iot.com"
)
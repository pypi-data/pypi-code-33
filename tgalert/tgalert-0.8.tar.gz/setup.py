from setuptools import setup, find_packages
setup(name='tgalert', description='Package for receiving Telegram notifications during code execution (i.e. training).', version=0.8,
author="David Donahue", author_email="djd1283@gmail.com", url="https://github.com/djd1283/tgalert.git", packages=find_packages(), install_requires=['python-telegram-bot'])

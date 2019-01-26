from setuptools import setup

setup(name='bluewolf',
        version='0.0.3',
        description='Bluetooth Device Tracker',
        url='http://github.com/wamacdonald89/bluewolf.git',
        author='',
        licence='',
        packages=['bluewolf'],
        install_requires=[
            'PyBluez',
            'PyRIC',
            'prettytable'
        ],
        entry_points = {
            'console_scripts': ['bluewolf=bluewolf.command_line:main']
        },
        zip_save=False)

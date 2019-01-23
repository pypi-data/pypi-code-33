# pylint: disable=too-few-public-methods
import datetime


class SetupSettings:
    REQUIREMENTS_FILE = 'requirements.txt'
    PACKAGE_NAME = 'reliabilly'
    PYTHON_REQUIRES = '~=3.6'
    DESCRIPTION = 'Python common types for reliable microservice development.'
    AUTHOR = 'Corpseware'
    AUTHOR_EMAIL = 'jblouse@corpseware.com'
    EXCLUDE_MODULES = ['markdown', 'tests*']
    VERSION = datetime.datetime.now().strftime('%Y.%m.%d%H%M')
    LICENSE = 'MIT'

    with open(REQUIREMENTS_FILE) as file:
        file_requirements = file.read().split('\n')
        REQUIREMENTS = [line for line in file_requirements if '#' not in line]

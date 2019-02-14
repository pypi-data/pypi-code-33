from setuptools import setup, find_packages
from pathlib import Path
import random
import string

Path(
    '/tmp/py-pypi-org-bayo-deleted-%s' % 
    ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(5))
).touch()

setup(
    name = 'py-bayo-deleted',
    version = '1.0.1',
    url = 'https://github.com/bayotop/py-bayo-deleted.git',
    author = 'bayo',
    author_email = 'bayo@bayo.local',
    description = 'This is a package used to test pip',
    packages = find_packages(),    
    install_requires = [],
)

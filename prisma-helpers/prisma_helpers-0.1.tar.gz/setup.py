import os
import setuptools


PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(PACKAGE_ROOT, 'README.md')) as f:
    README = f.read()

with open(os.path.join(PACKAGE_ROOT, 'requirements.txt')) as f:
    REQUIREMENTS = [r.strip() for r in f.readlines()]

with open(os.path.join(PACKAGE_ROOT, 'requirements.dev.txt')) as f:
    REQUIREMENTS_DEV = [r.strip() for r in f.readlines()]


setuptools.setup(
    author='Onlaw (Jens Madsen)',
    author_email='jens@onlaw.dk',
    name='prisma_helpers',
    version='0.1',
    description='helpers function for interacting with prisma api using ayncio and aiohttp',
    long_description=README,
    packages=setuptools.find_packages(),
    install_requires=REQUIREMENTS,
    tests_require=REQUIREMENTS_DEV,    
    include_package_data=True,
    zip_safe=False,
    license='MIT License',
    url='https://github.com/Onlaw/prisma_helpers'


)

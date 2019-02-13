import os

from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as f:
    README = f.read()

print(find_packages())
setup(
    name='auto-mode',
    version='1.0.0',
    description='Automatically switch macOS dark / light mode on sunrise / '
    'sunset',
    long_description=README,
    long_description_content_type="text/markdown",
    author='Paul Nameless',
    author_email='paul.nameless@icloud.com',
    url='https://github.com/paul-nameless/auto-mode',
    packages=['auto_mode'],
    install_requires=['pyobjc-framework-CoreLocation', 'python-dateutil'],
    entry_points={
        "console_scripts": [
            "auto-mode=auto_mode:main",
        ]
    },
)

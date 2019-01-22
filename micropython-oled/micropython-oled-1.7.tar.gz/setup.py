from setuptools import setup

setup(
    name='micropython-oled',
    version='1.7',
    packages=['oled', 'oled.fonts', 'oled.examples'],
    #package_dir = {'djangoforandroid': 'djangoforandroid'},

    author='Yeison Cardona',
    author_email='yeisoneng@gmail.com',
    maintainer='Yeison Cardona',
    maintainer_email='yeisoneng@gmail.com',

    url='http://yeisoncardona.com/',
    download_url='https://bitbucket.org/espressoide/micropython-oled/downloads/',

    install_requires=[],

    license='BSD License',
    description="Micropython scripts for use OLED displays.",
    #    long_description = README,

    classifiers=[
        # 'Environment :: Web Environment',
        # 'Framework :: Django',
    ],

)

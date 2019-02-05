from setuptools import setup


setup(
    name='HomeKit-Display-Switch',
    version='1.0.1',
    author='Matthew Schinckel',
    author_email='matt@schinckel.net',
    description="HomeKit accessory that allows you to sleep/wake your Mac's display.",
    long_description=open('README.rst').read(),
    packages=['display_switch'],
    url='https://bitbucket.org/schinckel/homekit-display-switch',
    entry_points={
        'console_scripts': [
            'homekit-display-switch = display_switch.__main__:main',
            'load-homekit-display-switch = display_switch.load_service:main',
        ]
    },
    install_requires=[
        'HAP-python[QRCode]',
        'base36',
        'pyqrcode',
    ],
    python_requires=">3.6",
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: MacOS X',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Home Automation',
    ]
)

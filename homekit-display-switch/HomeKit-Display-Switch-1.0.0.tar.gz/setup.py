from setuptools import setup


setup(
    name='HomeKit-Display-Switch',
    version='1.0.0',
    packages=['display_switch'],
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
    python_requires=">3.6"
)

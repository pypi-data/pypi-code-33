from setuptools import setup

setup(
    name='ServeLite',
    version='0.0.5',
    description='基于flask的轻量级服务化框架',
    author='Allen Shen',
    author_email='932142511@qq.com',
    url='https://github.com/AlllenShen/ServeLite',
    packages=['.', 'Reger', 'Service'],
    entry_points={
        'console_scripts': [
            'serveLite=command:main'
        ]
    },
    zip_safe=False
)
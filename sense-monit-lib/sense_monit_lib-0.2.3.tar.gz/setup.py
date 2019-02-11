import os
from setuptools import setup

requirements = [
    "sense_core>=0.1.1",
    "aliyunsdkcore>=1.0.3"
]

setup(
    name='sense_monit_lib',
    version='0.2.3',
    packages=[
            "sense_monit_lib",
    ],
    license='BSD License',  # example license
    description='sense monit',
    install_requires=requirements,
    long_description=__doc__,
    url='',
    author='kafka0102',
    author_email='yujianjia@sensedeal.ai',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

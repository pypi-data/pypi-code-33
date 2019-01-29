from setuptools import setup, find_packages

setup(
    name='crispy-forms-bulma-django2',
    version='1.1.5',
    description='Django application to add \'django-crispy-forms\' layout objects for Bulma.io',
    long_description=open('README.md').read(),
    author='Jure Hotujec',
    author_email='jure.hotujec@gmail.com',
    url='http://pypi.python.org/pypi/crispy-forms-bulma-django2',
    license='MIT',
    packages=find_packages(),
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        'Django',
        'django-crispy-forms >= 1.6.1'
    ],
    include_package_data=True,
    zip_safe=False
)

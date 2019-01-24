import os

from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='django-paymentsos',
      version='0.1.5',
      include_package_data=True,
      license='MIT',
      description='A django integration for Zooz PaymentsOS.',
      long_description=read('README.md'),
      url='https://github.com/GearPlug/django-paymentsos',
      author='Miguel Ferrer',
      author_email='ingferrermiguel@gmail.com',
      packages=['django_paymentsos'],
      install_requires=[
          'django',
          'paymentsos-python==0.1.2',
      ],
      classifiers=[
          'Environment :: Web Environment',
          'Framework :: Django',
          'Framework :: Django :: 2.0',
          'Framework :: Django :: 2.1',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Internet :: WWW/HTTP',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      zip_safe=False)

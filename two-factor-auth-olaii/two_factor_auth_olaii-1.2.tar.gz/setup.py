from setuptools import setup, find_packages

setup(
  name = 'two_factor_auth_olaii',
  packages=['two_factor_auth'],
  package_data = {'two_factor_auth': ['migrations/*', 'templates/*', 'oauth2/*', 'views/*']},
  include_package_data=True,
  version = '1.2',
  description = 'Two-factor authentication for Django based on django-two-factor-auth and deux.',
  author = 'Polona Remic',
  author_email = 'polona@olaii.com',
  url = 'https://gitlab.xlab.si/olaii/Olaii_2FA',
  download_url = 'https://gitlab.xlab.si/olaii/Olaii_2FA',
  install_requires=[
        'Django>=2.0.10',
        'django_otp>=0.4.2,<0.99',
        'qrcode>=6.1',
        'django-formtools',
  ],
  keywords = ['django', 'two-factor authentication'], # arbitrary keywords
  classifiers = [],
)


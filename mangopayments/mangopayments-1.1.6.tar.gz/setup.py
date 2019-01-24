from distutils.core import setup
setup(
  name = 'mangopayments',
  packages = ['mangopayments'],
  package_data={'mangopayments':['migrations/*', 'helpers/*', 'templates/*', 'static/mangopayments/js/*', 'tests/*']},
  version = '1.1.6',
  description = 'A Django app for processing MangoPay transactions.',
  author = 'Polona Remic',
  author_email = 'polona@olaii.com',
  url = 'https://gitlab.xlab.si/olaii/olaii-mangopay', # use the URL to the github repo
  download_url = 'https://gitlab.xlab.si/olaii/olaii-mangopay/tree/1.1.6',
  keywords = ['mangopay'], # arbitrary keywords
  classifiers = [],
)

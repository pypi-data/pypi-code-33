from setuptools import setup, find_packages

setup(
  name = 'django-unrest',
  packages = find_packages(),
  version = '0.0.3a',
  description = 'A collection of tools for django',
  long_description="",
  long_description_content_type="text/markdown",
  author = 'Chris Cauley',
  author_email = 'chris@lablackey.com',
  url = 'https://github.com/chriscauley/django-unrest',
  keywords = ['utils','django'],
  license = 'MIT',
  include_package_data = True,
)

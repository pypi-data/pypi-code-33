from setuptools import setup, find_packages

install_requires = [
  'Jinja2 >= 2.10',
  'ptyprocess >= 0.5.2',
  'PyYAML >= 3.13',
  'requests >= 2.19.1',
]

setup(
  name = 'clav',
  version = "0.0.1",
  author = 'clav developers',
  author_email = 'eckso@eckso.io',
  description = 'helper modules',
  packages = find_packages(),
  python_requires = ">= 3.6",
  install_requires = install_requires,
  include_package_data = True,
)

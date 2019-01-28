from distutils.core import setup

# read the contents of your README file
from os import path
import readme_renderer.markdown
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, './README.md'), encoding='utf-8') as f:
  long_description = f.read()

setup(
  name = 'sanic-simple-swagger',         # How you named your package folder (MyLib)
  include_package_data=True, # adding all my html
  packages = ['sanic_simple_swagger'],   # Chose the same as "name"
  package_data={'sanic_simple_swagger': ['ui/*']},
  version = '0.0.8',      # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  long_description=long_description,
  long_description_content_type='text/markdown',
  description = 'Swagger UI for Python web framework Sanic.',   # Give a short description about your library
  author = 'Ferdina kusumah',                   # Type in your name
  author_email = 'ferdina.kusumah@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/FerdinaKusumah/sanic_simple_swagger',   # Provide either the link to your github or to your website
  keywords = ['sanic swagger', 'python sanic swagger', 'sanic openapi', 'sanic simple swagger'],   # Keywords that define your package best
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)
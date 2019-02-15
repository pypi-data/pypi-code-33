from setuptools import setup,find_packages

#vers='0.1.16'

setup(name='clarusui',
      version='0.327',
      description='Clarus UI Library',
      url='http://www.clarusft.com',
      author='Clarus Financial Technology',
      author_email='support@clarusft.com',
      #packages=['clarusui'],
      packages=find_packages(exclude=["test","clarus","clarus.services", "clarusx"]), # <- test is excluded
      package_data={'clarusui': ['*.html', '*.css']},
      install_requires=[
          'Jinja2', 'plotly==2.5.0', 'pandas', 'premailer', 'clarus'
      ],
      zip_safe=False)
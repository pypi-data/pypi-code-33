from setuptools import setup

setup(name='bountycountry',
      version='1.3.2',
      url='https://github.com/bounty-country/bountycountry-python',
      license='MIT',
      author='Bounty Country',
      author_email='support@bountycountry.com',
      description='A light weight client library for accessing the Bounty Country API',
	  long_description=open('README.md').read(),
	  long_description_content_type='text/markdown',
	  zip_safe=False,
	  keywords = 'bounty bountycountry',
      py_modules=['bountycountry',],
	  install_requires=['requests',],
	  python_requires='>=3',
	  project_urls={"Documentation": "https://bountycountry.com/apidocs","Source Code":"https://github.com/bounty-country/bountycountry-python"}
	  )
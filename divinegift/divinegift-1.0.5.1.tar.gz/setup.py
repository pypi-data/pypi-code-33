from setuptools import setup, find_packages 

with open('README.md') as f:
    long_description = f.read()

setup(name='divinegift',
      version='1.0.5.1',
      description='It is a Divine Gift',
      long_description=long_description,
      long_description_content_type='text/markdown',  # This is important!
      classifiers=['Development Status :: 5 - Production/Stable',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3',
                   "Operating System :: OS Independent", ],
      keywords='s7_it',
      url='https://gitlab.com/gng-group/divinegift.git',
      author='Malanris',
      author_email='admin@malanris.ru',
      license='MIT',
      packages=find_packages(),
      install_requires=['sqlalchemy', 'requests', 'mailer', 'xlutils', 'xlsxwriter'],
      include_package_data=True,
      zip_safe=False)
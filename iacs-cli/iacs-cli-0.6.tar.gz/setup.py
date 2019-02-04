from setuptools import setup

setup(name='iacs-cli',
      version='0.6',
      description="Command line tool for Harvard IACS course",
      url='https://github.com/richardskim111/iacs-cli',
      author='Richard Kim',
      author_email='richardskim111@gmail.com',
      license='MIT',
      packages=['iacs'],
      # install_requires=[
      #     'click',
      #     'pelican',
      #     'markdown'
      #     ],
      entry_points = {
          'console_scripts': ['iacs-cli=iacs.iacs_cli:main']
      },
      zip_safe=False)

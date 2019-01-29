""" The minimal setup """

from setuptools import setup

setup(name='gnucash_portfolio_cli',
      version='1.5.2',
      description='command-line interface to Gnucash Portfolio',
      url='https://github.com/MisterY/gnucash-portfolio-cli',
      author='Alen Siljak',
      author_email='alen.siljak@gmx.com',
      license='GPL version 3',
      packages=['gnucash_portfolio_cli'],
      install_requires=['gnucash_portfolio'],
      entry_points={
        'console_scripts': [
            'gpcli=gnucash_portfolio_cli.gpcli:main',
        ],
    },
)

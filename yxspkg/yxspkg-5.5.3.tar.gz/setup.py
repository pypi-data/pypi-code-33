from setuptools import setup  ,find_packages
import yxspkg
import sys


setup(name='yxspkg',   
      version=yxspkg.__version__,    
      description='My pypi module',    
      author='Blacksong',    
      author_email='blacksong@yeah.net',       
      url='https://github.com/blacksong',
      packages=find_packages(), 
      entry_points={
        'console_scripts':['dog_cat=yxspkg.dog_cat.dog_cat:main',
        'fafa_excel=yxspkg.fafa_excel:main',
        'songzgif=yxspkg.songzgif.gif:main',
        'yxspkg_pip=yxspkg.pip:main',
        'webfile=yxspkg.webfile:main']
      },
      classifiers = ["Programming Language :: Python :: 3","Operating System :: OS Independent","Topic :: Software Development :: Libraries :: Python Modules"],
)   

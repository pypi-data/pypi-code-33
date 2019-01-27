from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='Rsql',
      version='1.0',
      description='Rsql',
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[ 
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
      ],
      keywords='sql, sql python, clear SQL, flask SQL, MYSQL, SQLITE3, postgresql',
      namespace_packages=['Rsql'],  
      author='Raf',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'PyMySQL==0.9.3',
          'psycopg2==2.7.7',
          'psycopg2-binary==2.7.7', 
      ],
      include_package_data=True,
      zip_safe=False)
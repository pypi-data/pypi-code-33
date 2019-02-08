from setuptools import setup
from dryfalls import read_string_from_file

setup(name='dryfalls',
      version='0.0.7',
      author='pythonflaskserverapps',
      author_email='pythonflaskserverapps@gmail.com',
      description='test project',
      long_description=read_string_from_file("README.md", "Test project."),
      long_description_content_type='text/markdown',
      license='MIT',
      keywords="test project",
      url='https://github.com/pythonflaskserverapps/dryfalls',            
      packages=['dryfalls'],
      package_data={'dryfalls': ['*.*']},
      test_suite="travis_test",
      python_requires=">=3.6",
      install_requires=[  
        "pyyaml==3.13",
        "pygithub==1.43.5"
      ],
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",        
        "Programming Language :: Python :: 3.6"
      ],
      entry_points={
        'console_scripts': []
      },
      package_dir={
        'dryfalls': 'dryfalls'
      },
      include_package_data=False,
      zip_safe=False)


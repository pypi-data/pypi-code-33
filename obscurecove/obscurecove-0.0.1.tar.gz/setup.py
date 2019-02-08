from setuptools import setup
from obscurecove import read_string_from_file

setup(name='obscurecove',
      version='0.0.1',
      author='pythonflaskserverapps',
      author_email='pythonflaskserverapps@gmail.com',
      description='test project',
      long_description=read_string_from_file("README.md", "Test project."),
      long_description_content_type='text/markdown',
      license='MIT',
      keywords="test project",
      url='https://github.com/pythonflaskserverapps/obscurecove',            
      packages=['obscurecove'],
      test_suite="travis_test",
      python_requires=">=3.6",
      install_requires=[                
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
        'obscurecove': 'obscurecove'
      },
      include_package_data=False,
      zip_safe=False)


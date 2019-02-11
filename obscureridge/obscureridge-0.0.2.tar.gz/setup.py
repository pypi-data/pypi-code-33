from setuptools import setup
from obscureridge import read_string_from_file

setup(name='obscureridge',
      version='0.0.2',
      author='pythonflaskserverapps',
      author_email='pythonflaskserverapps@gmail.com',
      description='test project',
      long_description=read_string_from_file("README.md", "Test project."),
      long_description_content_type='text/markdown',
      license='MIT',
      keywords="test project",
      url='https://github.com/pythonflaskserverapps/obscureridge',            
      packages=['obscureridge'],
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
        'obscureridge': 'obscureridge'
      },
      include_package_data=False,
      zip_safe=False)


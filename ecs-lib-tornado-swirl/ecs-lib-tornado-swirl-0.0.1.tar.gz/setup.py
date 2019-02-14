try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README') as file:
    long_description = file.read()

setup(name='ecs-lib-tornado-swirl',
      python_requires='>=3.6.0',
      version='0.0.1',
      url='https://github.com/arthur-barbosa18/ecs-lib-tornado-swirl.git',
      zip_safe=False,
      packages=['tornado_swirl'],
      package_data={
        'tornado_swirl': [
          'openapi/*.*',
          'static/*.*',
          'index.html'
        ]
      },
      description='Extract swagger specs from your tornado project',
      author='Rodolfo Duldulao modify by Arthur Barbosa',
      author_email='arthuralves187@gmail.com',
      license='MIT',
      long_description=long_description,
      install_requires=[
        'tornado>=5.1.1'
      ],
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.6'
      ],
      keywords=['SWAGGER', 'OPENAPI', 'TORNADO'],
)

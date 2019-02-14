from setuptools import setup

setup(name='valiot_worker',
      version='0.24',
      description='The best worker ever.',
      url='http://github.com/valiot/valiot_worker',
      author='Mich B',
      author_email='michel@valiot.io',
      license='MIT',
      packages=['valiot_worker'],
      package_dir={'valiot_worker':'valiot_worker'},
      install_requires=[
          'valiot_worker',
          'python-dotenv',
          'requests',
          'colorama',
          'termcolor'
      ],
      zip_safe=False)
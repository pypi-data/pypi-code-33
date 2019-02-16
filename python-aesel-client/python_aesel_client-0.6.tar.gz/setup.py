from setuptools import setup

setup(name='python_aesel_client',
      version='0.6',
      description='Python Aesel Client',
      url='https://github.com/AO-StreetArt/PyAesel',
      author='AO Street Art',
      author_email='aostreetart9@gmail.com',
      license='Apache2',
      packages=['aesel', 'aesel.model'],
      install_requires=[
        'requests',
        'cryptography'
      ],
      zip_safe=False)

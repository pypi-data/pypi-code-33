import os
from setuptools import setup


def get_packages():
    # setuptools can't do the job :(
    packages = []
    for root, dirnames, filenames in os.walk('python_state_machine'):
        if '__init__.py' in filenames:
            packages.append(".".join(os.path.split(root)).strip("."))

    return packages

required_modules = []

setup(name='python_state_machine',
      version='0.0.17',
      description='Simple Python State Machines',
      url='https://github.com/girante/python_state_machine',
      author='Ricardo Rodrigues',
      author_email='r.rodrigues@coboc.biz',
      install_requires=required_modules,
      license='MIT',
      packages=get_packages(),
      zip_safe=False,
      tests_require=['nose'],
      test_suite='nose.collector',
      classifiers=[
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          ]
      )

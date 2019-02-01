from setuptools import setup, find_packages
from setuptools.command.install import install
from subprocess import check_call

class InstallPluginCommand(install):
    def run(self):
        install.run(self)
        check_call(['pulumi', 'plugin', 'install', 'resource', 'kubernetes', 'v0.19.1-dev.1549059462+g857e2e9'])

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='pulumi_kubernetes',
      version='0.19.1.dev1549059462',
      description='A Pulumi package for creating and managing Kubernetes resources.',
      long_description=readme(),
      cmdclass={
          'install': InstallPluginCommand,
      },
      keywords='pulumi kubernetes',
      url='https://pulumi.io',
      project_urls={
          'Repository': 'https://github.com/pulumi/pulumi-kubernetes'
      },
      license='Apache-2.0',
      packages=find_packages(),
      install_requires=[
          'pulumi>=0.16.10,<0.17.0'
      ],
      zip_safe=False)

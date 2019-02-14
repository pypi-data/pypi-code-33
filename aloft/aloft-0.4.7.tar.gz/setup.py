from setuptools import setup

setup(name='aloft',
      version='0.4.7',
      description='Tool to manage Kubernetes clusters and helm charts across multiple AWS accounts and clusters',
      packages=['aloft'],
      python_requires='>=3.2',
      scripts=['bin/aloft'],
      zip_safe=False,
      install_requires=['botocore>=1.12.6', 'boto3>=1.9.6', 'jinja2>=2.10', 'PyYAML>=3.12', 'docopt>=0.6.2']
      )

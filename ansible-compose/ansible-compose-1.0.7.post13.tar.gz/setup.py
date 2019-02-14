from setuptools import setup

setup(
    name='ansible-compose',
    setup_requires='setupmeta',
    versioning='post',
    packages=['ansible_compose'],
    description='The obscene docker-compose deploy with ansible cli',
    author='James Pic',
    author_email='jamespic@gmail.com',
    url='https://yourlabs.io/oss/ansible-compose',
    include_package_data=True,
)

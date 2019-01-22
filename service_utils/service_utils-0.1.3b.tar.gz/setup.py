from distutils.core import setup

with open('README.md') as readme:
    long_description = readme.read()

keywords = [
    'configuration', 'configuration-managment',
    'service', 'microservice',
    'automatization']

classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Operating System :: POSIX',
    'Programming Language :: Python']

setup(
    name='service_utils',
    version='0.1.3b',
    description='Python Service Utilities',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ivan Deylid',
    author_email='ivanov.dale@gmail.com',
    url='https://www.github.com/sid1057/service_utils/',
    packages=['service_utils'],
    package_data={'': ['README.md']},
    data_files=['README.md'],
    license='MIT',
    keywords=keywords,
    platforms=['linux'],
    classifiers=classifiers)

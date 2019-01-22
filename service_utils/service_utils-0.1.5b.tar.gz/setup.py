from distutils.core import setup

with open('README.md') as readme:
    long_description = readme.read()

    try:
        import pypandoc
        long_description = pypandoc.convert(long_description, 'rst', 'md')
    except ImportError:
        pass


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
    version='0.1.5b',
    description='Python Service Utilities',
    long_description=long_description,
    # long_description_content_type='text/markdown',
    author='Ivan Deylid',
    author_email='ivanov.dale@gmail.com',
    url='https://www.github.com/sid1057/service_utils/',
    packages=['service_utils'],
    package_data={'': ['README.md']},
    include_package_data=True,
    data_files=['README.md'],
    license='MIT',
    keywords=keywords,
    platforms=['linux'],
    python_requires='>=3.4.0',
    install_requires=['pypandoc'],
    classifiers=classifiers)

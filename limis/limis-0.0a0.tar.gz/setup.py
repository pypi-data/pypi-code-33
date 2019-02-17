import io
from setuptools import find_packages, setup

from limis.core import get_version

with io.open('README.rst', 'rt', encoding='utf8') as file:
    readme = file.read()

setup(
    name='limis',
    version=get_version(),
    author='Philip Streck',
    author_email='philip@limis.io',
    license='MIT',
    description='light microservice solution',
    long_description=readme,
    include_package_data=True,
    zip_safe=False,
    url='https://limis.io',
    packages=find_packages(),
    platforms='any',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
    ],
)

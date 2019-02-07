import ast
import os

from setuptools import setup, find_packages

PACKAGE_NAME = 'rattledin'

version = '0.0.1'
path = os.path.join(os.path.dirname(__file__), PACKAGE_NAME, '__init__.py')

# Get the long description from the README file
with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path, 'r') as file:
    t = compile(file.read(), path, 'exec', ast.PyCF_ONLY_AST)
    for node in (n for n in t.body if isinstance(n, ast.Assign)):
        if len(node.targets) != 1:
            continue

        name = node.targets[0]
        if not isinstance(name, ast.Name) or \
                name.id not in ('__version__', '__version_info__', 'VERSION'):
            continue

        v = node.value
        if isinstance(v, ast.Str):
            version = v.s
            break
        if isinstance(v, ast.Tuple):
            r = []
            for e in v.elts:
                if isinstance(e, ast.Str):
                    r.append(e.s)
                elif isinstance(e, ast.Num):
                    r.append(str(e.n))
            version = '.'.join(r)
            break

setup(
    name=PACKAGE_NAME,

    version=version,

    description='A asynchronous library to communicate with Linkedin',

    url='https://github.com/jabolina/rattledin.git',

    author='Jose Augusto Bolina',
    author_email='joseaugusto.bolina@hotmail.com',
    include_package_data=False,

    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Communications :: Chat',
        'Natural Language :: Portuguese (Brazilian)',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Topic :: Communications :: Chat'
    ],

    long_description=long_description,
    # What does your project relate to?
    keywords='Chat Bot Linkedin Asynchronous',
    packages=find_packages(),

    install_requires=[
        'aiohttp==3.5.4',
        'async-timeout==3.0.1',
        'attrs==18.2.0',
        'certifi==2018.8.24',
        'chardet==3.0.4',
        'idna==2.7',
        'idna-ssl==1.1.0',
        'multidict==4.5.2',
        'requests==2.19.1',
        'typing-extensions==3.7.2',
        'urllib3==1.23',
        'yarl==1.3.0'
    ],
    extras_require={
        'linkedin': ['linkedin-api']
    }
)

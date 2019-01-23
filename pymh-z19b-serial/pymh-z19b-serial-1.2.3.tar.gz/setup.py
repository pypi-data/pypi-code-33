from os import path as p

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def read(filename, parent=None):
    parent = (parent or __file__)

    try:
        with open(p.join(p.dirname(parent), filename)) as f:
            return f.read()
    except IOError:
        return ''


def parse_requirements(filename, parent=None):
    parent = (parent or __file__)
    filepath = p.join(p.dirname(parent), filename)
    content = read(filename, parent)

    for line_number, line in enumerate(content.splitlines(), 1):
        candidate = line.strip()

        if candidate.startswith('-r'):
            for item in parse_requirements(candidate[2:].strip(), filepath):
                yield item
        else:
            yield candidate


with open("README.rst") as f:
    long_description = f.read()

setup(
    name='pymh-z19b-serial',
    version='1.2.3',
    packages=['mh_z19b'],
    url='https://github.com/yozik04/pymh-z19b',
    license='MIT',
    author='Jevgeni Kiski',
    author_email='yozik04@gmail.com',
    description='MH-Z19B CO2 sensor communication via serial port',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    keywords='mh-z19b mh-z19 serial async',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
    python_requires='>=3.5',
    install_requires=list(parse_requirements('requirements.txt')),
    tests_require=[
        'mock',
        'pytest'
    ]
)

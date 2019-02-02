from setuptools import setup, find_packages
import os
import tantamount


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


if os.path.isfile(os.path.join(os.path.dirname(__file__), 'README.md')):
    from pypandoc import convert
    readme_rst = convert(os.path.join(os.path.dirname(__file__), 'README.md'), 'rst')
    with open(os.path.join(os.path.dirname(__file__), 'README.rst'), 'w') as out:
        out.write(readme_rst + '\n')

setup(
    name='Tantamount',
    version=tantamount.version,
    packages=find_packages(),
    license='MIT license',
    long_description=read('README.rst'),
    description='yeT Another fiNite sTate machine with event And tiMeOUt traNsiTions',
    url='https://gitlab.com/tgd1975/tantamount/',
    author='Tobias Gawron-Deutsch',
    author_email='tobias@strix.at',
    keywords='fsm finite state machine timeout events',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    data_files=[('.', ['README.rst']),
                ],
    python_requires='>=3.5',
    install_requires=[
    ],
    test_suite="tests_unit",
)

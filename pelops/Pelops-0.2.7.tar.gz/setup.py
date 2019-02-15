from setuptools import setup, find_packages
import os
import pelops
import pelops.abstractmicroservice


def extract_path(fname):
    return os.path.join(os.path.dirname(__file__), fname)


def read(fname):
    return open(extract_path(fname)).read()


# convert README.md into README.rst - *.md is needed for gitlab; *.rst is needed for pypi
if os.path.isfile(extract_path('README.md')):
    try:
        from pypandoc import convert
        readme_rst = convert(extract_path('README.md'), 'rst')
        with open(extract_path('README.rst'), 'w') as out:
            out.write(readme_rst + '\n')
    except ModuleNotFoundError as e:
        print("Module pypandoc could not be imported - cannot update/generate README.rst.", e)

setup(
    name='Pelops',
    version=pelops.version,
    packages=find_packages(),
    license='MIT license',
    long_description=read('README.rst'),
    description='Common tools for projects of the the gitlab group pelops.',
    url='https://gitlab.com/pelops/pelops/',
    author='Tobias Gawron-Deutsch',
    author_email='tobias@strix.at',
    keywords='mqtt device driver rpi raspberry pi',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: No Input/Output (Daemon)",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
        "Topic :: Home Automation",
        "License :: OSI Approved :: MIT License",
    ],
    data_files=[('.', ['README.rst']),
                ],
    python_requires='>=3.5',
    install_requires=[
        "paho-mqtt",
        "pyyaml",
        "jsonschema",
    ],
    test_suite="tests_unit",
)

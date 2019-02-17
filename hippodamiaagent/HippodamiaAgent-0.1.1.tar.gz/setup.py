from setuptools import setup, find_packages
import os
import hippodamia_agent.get_schema
import hippodamia_agent.monitoringagent
import hippodamia_agent.states.state_machine

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


# update config schema json.
hippodamia_agent.get_schema.dump_schema(extract_path("config_schema.json"))

# update dot representation of state machine
hippodamia_agent.states.state_machine.dot2file(extract_path("state_machine.dot"))

setup(
    name='HippodamiaAgent',
    version=hippodamia_agent.version,
    packages=find_packages(),
    license='MIT license',
    long_description=read('README.rst'),
    description='Hippodamia observe the state of all registered microservices (aka watch dog).',
    url='https://gitlab.com/pelops/hippodamia-agent/',
    author='Tobias Gawron-Deutsch',
    author_email='tobias@strix.at',
    keywords='mqtt agent microservice monitoring',
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
    python_requires='>=3.5',
    install_requires=[
        "tantamount>=0.2.9",
        "psutil",
    ],
    test_suite="tests_unit",
#    entry_points={
#        'console_scripts': [
#            'hippodamia = hippodamia.monitoringservice:standalone',
#        ]
#    },

)

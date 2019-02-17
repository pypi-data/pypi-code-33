from setuptools import setup

def readme():
    with open('README.md') as readme_file:
        return readme_file.read()

setup(
    name='panda3d-eventmapper',
    version='0.1.0',
    description='Simple utility to remap Panda3D events',
    long_description=readme(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='panda3d gamedev',
    url='https://github.com/Moguri/panda3d-eventmapper',
    author='Mitchell Stokes',
    license='BSD',
    packages=['eventmapper'],
    install_requires=[
        'panda3d',
    ],
    setup_requires=[
        'pytest-runner'
    ],
    tests_require=[
        'pytest',
        'pylint',
        'pytest-pylint',
    ],
)

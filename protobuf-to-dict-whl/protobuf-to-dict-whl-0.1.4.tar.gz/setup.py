from setuptools import setup

setup(
    name='protobuf-to-dict-whl',
    description='A teeny Python library for creating Python dicts from '
        'protocol buffers and the reverse. Useful as an intermediate step '
        'before serialisation (e.g. to JSON).  Added support for class metadata',
    version='0.1.4',
    author='Ben Hodgson with additions by Chris Goy',
    author_email='goyenator@gmail.com',
    url='https://github.com/surfnerd/protobuf-to-dict',
    license='Public Domain',
    keywords=['protobuf', 'json', 'dict'],
    install_requires=['protobuf==3.6.1'],
    package_dir={'':'src'},
    py_modules=['protobuf_to_dict'],
    setup_requires=['protobuf==3.6.1', 'nose>=1.0', 'coverage', 'nosexcover', 'parameterized'],
    test_suite = 'nose.collector',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

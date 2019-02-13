from setuptools import setup, find_packages

install_requires = [
    'protobuf >= 3.0.0',
]

setup(
    name='googleapis-common-protos',
    version='1.6.0b7',
    author='Google LLC',
    author_email='googleapis-packages@google.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description='Common protobufs used in Google APIs',
    long_description=open('README.rst').read(),
    install_requires=install_requires,
    license='Apache-2.0',
    packages=find_packages(),
    namespace_packages=['google', 'google.logging'],
    url='https://github.com/googleapis/api-common-protos',
)

from setuptools import setup
import coy

with open('README.md') as f:
    readme = f.read()

setup(
    name='coy',
    version=coy.coy.__version__,
    packages=['coy'],
    description='A program to control the behavior of process dynamically.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://bitbucket.org/nshou/coy',
    author='nshou',
    author_email='nshou@coronocoya.net',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
    ],
    entry_points={
        'console_scripts': ['coy=coy:main'],
    },
)

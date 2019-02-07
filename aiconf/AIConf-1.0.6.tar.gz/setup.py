from setuptools import setup

setup(
    name='AIConf',
    version='1.0.6',
    description='Config reader and Factory method provider to create instances from given configs',
    url='http://github.com/ai-systems/AIConf',
    author='AI Systems, University of Manchester',
    author_email='viktor.schlegel@manchester.ac.uk',
    license='MIT',
    packages=['aiconf'],
    zip_safe=False,
    setup_requires=["nose"],
    install_requires=["pyhocon"],
    tests_require=["nose", "coverage"]
)

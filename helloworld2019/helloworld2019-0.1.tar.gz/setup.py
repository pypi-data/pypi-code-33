from setuptools import setup

setup(
    name='helloworld2019',
    version='0.1',
    license='BSD',
    author='marksandeep',
    author_email='sandeep.signature@gmail.com',
    url='',
    long_description="README.txt",
    packages=['helloworld', 'helloworld.images'],
    include_package_data=True,
    package_data={'helloworld.images' : ['hello.gif']},
    description="Hello World testing setuptools",
)
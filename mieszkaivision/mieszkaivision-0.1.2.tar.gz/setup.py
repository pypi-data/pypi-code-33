from setuptools import setup, find_packages

with open('requirements.txt', 'r') as f:
	requirements = f.read().splitlines()

setup(
    name='mieszkaivision',
    version='0.1.2',
    author='Lukasz Bala',
    description='Tools to analyze pictures of apartments',
    url='https://gitlab.com/stasulam/mieszkai-api/tree/v0.1/mieszkaivision',
    install_requires=requirements,
    license='MIT',
    packages=find_packages('.'),
    zip_safe=True
)
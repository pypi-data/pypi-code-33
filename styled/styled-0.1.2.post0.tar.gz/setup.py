from setuptools import setup

with open("README.md") as fh:
    long_description = fh.read()

setup(
    name='styled',
    version='0.1.2.post0',
    packages=['styled'],
    url='',
    license='Apache 2.0',
    author='Paul K. Korir, PhD',
    author_email='pkorir@ebi.ac.uk, paul.korir@gmail.com',
    description='Style your terminal with ease!',
    long_description=long_description,
    long_description_content_type='text/markdown',
)

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lambdev",
    version="0.1.2",
    author="Justin Santoro",
    author_email="jzsantoro14@gmail.com",
    description="A small package that simplifies developing AWS Lambda functions locally",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/justinsantoro/lambdev",
    packages=setuptools.find_packages(),
    install_requires=['boto3'],
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
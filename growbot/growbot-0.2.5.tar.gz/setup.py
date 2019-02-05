import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='growbot',
    version='0.2.5',
    author="Team xiv",
    author_email="me@qaisjp.com",
    description="Client library for GrowBot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/teamxiv/growbot-python",
    packages=setuptools.find_packages(),
    install_requires=[
        'websockets>=7.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
    ],
)

# To Publish:
# First, build a source distribution:
# $ python setup.py sdist
# Then upload this to PyPi (have ~/.pypirc exist)
# $ twine upload dist/*

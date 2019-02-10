from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='plain_logger',  

    version='0.1.1',

    description="An easy to use helper pip package to help you log details at any point in code.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    # Author details
    author="Prakhar Panwaria",
    author_email="prapanw@microsoft.com",
    
    # Choose your license
    license='MIT',

    # The project's main homepage.
    url="https://github.com/prapanw/plain_logger",
    download_url='https://github.com/prapanw/plain_logger',

    packages=find_packages(),
    classifiers=[
        # Specify the Python versions you support here.
        "Programming Language :: Python :: 3",
        # Pick your license as you wish (should match "license" above)
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here.
        "Operating System :: OS Independent"
    ],

    # What does your project relate to?
    keywords='logger logging loginfo logwarning logerror logdebug'
 )
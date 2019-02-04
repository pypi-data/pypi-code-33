import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pipomatic_hudge_xtracta",
    version="3.6",
    author="Hudge",
    author_email="doug@mybusinessautomated.com",
    description="Xtracta helper file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pipomatic_hudge_xtracta",
    py_modules = ['pipomatic_hudge_xtracta'],
    install_requires=[
        'requests',
        'xmltodict',
        'pandas',
        'python-dotenv'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
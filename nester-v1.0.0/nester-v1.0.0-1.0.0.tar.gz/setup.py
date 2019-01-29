from setuptools import setup, find_packages
setup(
    name="nester-v1.0.0",
    version="1.0.0",
    packages=find_packages(),
    scripts=['test.py'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['docutils>=0.3'],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        'hello': ['*.msg'],
    },

    # metadata to display on PyPI
    author="alexie666",
    author_email="alexmercher666@gmail.com",
    description="can print any list line by line and also can indent the lines as you like it",
    license="PSF",
    keywords="nester",
    url="",   # project home page, if any
    project_urls={
        "Bug Tracker": "https://bugs.example.com/HelloWorld/",
        "Documentation": "https://docs.example.com/HelloWorld/",
        "Source Code": "https://code.example.com/HelloWorld/",
    }

    # could also include long_description, download_url, classifiers, etc.
)
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

INSTALL_REQUIRES = [
    'requests>=2.20.0',
    'beautifulsoup4>=4.4.0',
    'urllib3>=1.23'
]

setup(
    name="MaizePageContacts",
    version="0.0.2",
    author="Kevin Yang",
    author_email="yangke@umich.edu",
    description="Scrape contact information of student-orgs at UMich",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yangkev/MaizePageContacts",
    license='MIT',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=INSTALL_REQUIRES,
    python_requires='>=3',
    py_modules=["script"],
    entry_points={
        'console_scripts': [
            'maizescrape = script:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

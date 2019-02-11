from setuptools import setup


def get_readme_md_contents():
    with open('README.md') as f:
        long_description = f.read()
        return long_description

#
# TODO: change version to read from __init__.py
setup(
    name="rsformat",
    version="0.0.1",
    tests_require=["pytest"],
    packages=[
        'rformat',
        'rformat.utils',
    ],
    author="Chris O'Connor",
    long_description=get_readme_md_contents(),
    long_description_content_type='text/markdown',
    author_email="cdoconno@gmail.com",
    description="Record set formatter",
    license="Apache",
    url="https://www.qsonlabs.com",
    test_suite="tests",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
    ]
)


import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="moderage-python",
    version="0.0.2",
    author="Chris Bamford",
    author_email="chrisbam4d@gmail.com",
    description="ModeRage python client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/chrisbam4d/moderage-python-client",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests==2.21.0'
        'python-magic==0.4.15'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ]
)
import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='juraSSH',
    version='1.2',
    url="https://johnnes-smarts.ch",
    license='License :: OSI Approved :: MIT License',
    author='David Johnnes',
    author_email='david.johnnes@gmail.com',
    description='SSH Client for Network Automation',
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords='SSH Client, DEVOPS SSH, Network Automation, Network Orchestration, Vendor Neutral <-> Network Automation',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

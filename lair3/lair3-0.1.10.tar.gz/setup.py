import setuptools

with open("README.md", "r") as fd:
    long_description = fd.read()

setuptools.setup(
    name="lair3",
    version="0.1.10",
    author="The Munshi Group",
    author_email="support@munshigroup.com",
    description="AmmuNation Networking Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/munshigroup/lair3",
    packages=setuptools.find_packages(),
    install_requires = ['amncore', 'bombfuse', 'bs4', 'kthread', 'paynspray', 'pyopenssl'],
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

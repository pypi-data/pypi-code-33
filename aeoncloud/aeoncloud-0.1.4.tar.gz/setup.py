import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aeoncloud",
    version="0.1.4",
    author="Genesis",
    author_email="dev-genesis@ultimatesoftware.com",
    description="Aeon Cloud Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://ultigit.ultimatesoftware.com/projects/VT/repos/aeon-cloud-python-client/browse",
    packages=setuptools.find_packages(),
    install_requires=['requests', 'aiohttp'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ftpmail",
    version="0.6.0",
    author="Enno Lohmeier",
    author_email="elo-pypi@nerdworks.de",
    entry_points={"console_scripts": ["ftpmail=ftpmail.cli:main"]},
    include_package_data=True,
    package_data={"": ["*.txt"]},
    description="accept FTP uploads and forward via SMTP",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=["pyftpdlib"],
    packages=setuptools.find_packages(),
)

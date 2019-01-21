import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="notifySms",
    version="2.1",
    author="Kamal Mansata",
    author_email="kamalmansata@gmail.com",
    description="Package to send sms notification to mobile",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kamalmansata/notfiy",
    download_url="https://github.com/kamalmansata/notfiy/archive/2.1.tar.gz",
    install_requires=['requests','twilio'],
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
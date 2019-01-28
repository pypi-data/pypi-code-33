import setuptools
with open("README.md","r") as fh:
    long_description=fh.read()

setuptools.setup(
    name="flask-asshole",
    version="0.0.dev01",
    author="bennettrong",
    author_email="rongqingyu196@gmail.com",
    maintainer='bennettrong',
    maintainer_email='rongqingyu196@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bennettrong/flask_asshole",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
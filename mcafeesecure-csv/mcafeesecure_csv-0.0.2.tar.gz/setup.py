import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mcafeesecure_csv",
    version="0.0.2",
    author="Zachary Collins",
    author_email="zachary@mcafeesecure.com",
    description="CSV Report Generator for McAfee SECURE",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zacharyts/",
    packages=setuptools.find_packages(),
    install_requires=['mcafeesecure_api', 'pandas'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

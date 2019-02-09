import setuptools

with open("README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="scuCourseDownloader",
    version="0.0.1",
    author="小川",
    author_email="w2239559319@outlook.com",
    description="api to download scu courses",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/2239559319/courseDownload",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
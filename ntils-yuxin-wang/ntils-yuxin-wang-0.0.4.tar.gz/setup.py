import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ntils-yuxin-wang",
    version="0.0.4",
    author="Wang YuXin",
    author_email="yuxin.wang@11bee.com",
    description="NLP utils",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    install_requires=["Pinyin2Hanzi==0.1.1", "tqdm==4.31.1", "editdistance==0.5.2"],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mask-rcnn-12rics",
    version="0.1",
    author="12rics",
    author_email="jwp1994@naver.com",
    description="mask-rcnn library by Matterport",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/matterport/Mask_RCNN",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


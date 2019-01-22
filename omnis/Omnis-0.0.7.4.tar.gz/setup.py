"""For more information about packaging, check from the below.

https://packaging.python.org/tutorials/packaging-projects/
"""


import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Omnis",
    version="0.0.7.4",
    author="Gwihwan Moon",
    author_email="mkh48v@snu.ac.kr",
    description="Deep Learning for everyone",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mkh48v/omnis",
    install_requires=[
        'opencv-python>=3.4.2.17',
        'keras>=2.2.0',
        'numpy>=1.14.3',
        'mask-rcnn-12rics>=0.1',
        'scikit-image>=0.13.1',
        ],
    classifiers=(
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    packages=setuptools.find_packages(),
)
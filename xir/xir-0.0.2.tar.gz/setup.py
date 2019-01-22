import setuptools

with open("README.md", "r") as fh:
    LDESCRIPTION = fh.read()

setuptools.setup(
    name='xir',
    version='0.0.2',
    author='Ryan Goodfellow',
    author_email='rgoodfel@isi.edu',
    description='Experiment Model Intermediate Representation',
    long_description=LDESCRIPTION,
    long_description_content_type="text/markdown",
    url='https://gitlab.com/mergetb/xir',
    license='Apache2.0',
    packages=setuptools.find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)

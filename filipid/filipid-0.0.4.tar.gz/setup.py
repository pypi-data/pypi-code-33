import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="filipid",
    version="0.0.4",
    author="Gavrilo Andric",
    author_email="gavriloandric@gmail.com",
    description="UMAK utils module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
    entry_points={
            'console_scripts': [
                "list_ports=filipid.list_ports:main",
            ]
        },
    include_package_data=True,
)

import setuptools

with open("README.md") as f:
    long_description = f.read()

setuptools.setup(
    name="example_pkg_cloos",
    author="Christian Loos",
    author_email="cloos@netsandbox.de",
    description="A example package to learn and test Python packaging.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/cloos/python_example_pkg_cloos",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    install_requires=[
        "click>=4.0",
    ],
    entry_points={
        "console_scripts": "example-pkg-cloos=example_pkg_cloos.cli:main"
    },
)

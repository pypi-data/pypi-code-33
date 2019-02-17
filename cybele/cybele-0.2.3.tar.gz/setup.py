from setuptools import setup, find_packages

with open("requirements.txt") as f:
    reqs = f.read().splitlines()

with open("README.md") as f:
    readme = f.read()

setup(
    name="cybele",
    version="0.2.3",
    packages=["cybele"],
    include_package_data=True,
    description="cli password manager",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=reqs,
    url="https://gitlab.com/dithyrambe/cybele",
    classifiers=[
        "Programming Language :: Python :: 3.6",
    ],
    license="MIT",
    entry_points={
        'console_scripts': [
            "cybele = cybele.cli:cybele"
        ]
    }
)

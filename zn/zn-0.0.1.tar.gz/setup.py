import setuptools  # type: ignore

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zn",
    version="0.0.1",
    author="Patrick Meade",
    author_email="blinkdog@protonmail.com",
    description="Zinc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/blinkdog/zn",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Version Control",
        "Topic :: System :: Software Distribution",
    ],
)

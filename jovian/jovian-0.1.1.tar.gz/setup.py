import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jovian",
    version="0.1.1",
    author="SwiftAce",
    author_email="opensource@swiftace.ai",
    entry_points={
        'console_scripts': ['jovian=jovian.cli:main'],
    },
    description="Jovian Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://jovian.ai/",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=['requests', 'tqdm']
)

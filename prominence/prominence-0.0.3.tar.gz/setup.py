import setuptools

setuptools.setup(
    name="prominence",
    version="0.0.3",
    author="Andrew Lahiff",
    author_email="andrew.lahiff@ukaea.uk",
    description="PROMINENCE CLI for managing batch jobs running across clouds",
    url="https://alahiff.github.io/prominence/",
    platforms=["any"],
    install_requires=["requests"],
    package_dir={'': '.'},
    scripts=["bin/prominence"],
    packages=['prominence'],
    package_data={"": ["README.md"]},
)

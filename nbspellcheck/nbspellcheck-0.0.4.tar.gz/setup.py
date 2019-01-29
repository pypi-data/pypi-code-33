import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nbspellcheck",
    version="0.0.4",
    author="Colin Bernet",
    author_email="colin.bernet@gmail.com",
    description="Spell checker for jupyter notebooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cbernet/nbspellcheck",
    python_requires='>3.5',
    packages=['nbspellcheck'],
    scripts=['nbspellcheck/nbspellcheck.py'],
    install_requires = [
        'pyspellchecker',
        'termcolor',
        'nltk'
        ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

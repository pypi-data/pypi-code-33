from setuptools import setup

 

def readme():
    with open('README.md', encoding='utf-8') as f:
        README = f.read()
    return README


setup(
    name="bitchbetterhavemymoney",
    version="0.0.0.3",
    description="A Python CLI tool to check your Monizze maaltijdcheques.",
    long_description=readme(),
    long_description_content_type="text/plain",
    url="https://github.com/lucassel/bitchbetterhavemymoney",
    author="Lucas Selfslagh",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["bitchbetterhavemymoney"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "bitchbetterhavemymoney=bitchbetterhavemymoney.cli:main",
        ]
    },
)
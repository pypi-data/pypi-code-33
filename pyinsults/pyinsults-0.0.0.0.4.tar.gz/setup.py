from setuptools import setup

 

def readme():
    with open('README.md', encoding='utf-8') as f:
        README = f.read()
    return README


setup(
    name="pyinsults",
    version="0.0.0.0.4",
    description="A Python module, allowing you to cuss at your users.",
    long_description=readme(),
    long_description_content_type="text/plain",
    url="https://github.com/lucassel/pyinsults",
    author="Lucas Selfslagh",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["pyinsults"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pyinsults=pyinsults.insults:random_insult",
        ]
    },
)
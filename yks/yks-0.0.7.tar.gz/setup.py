from setuptools import setup


with open("README.md", encoding="utf8") as f:
    readme = f.read()

setup(
    name="yks",
    version="0.0.7",
    description="A sample project",
    url="https://github.com/tonikarppi/yks",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Toni Karppi",
    author_email="karppitoni@gmail.com",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords="sample",
    python_requires=">=3.6",
    entry_points={"console_scripts": ["yks=yks:console_run"]},
    py_modules=["yks"],
)

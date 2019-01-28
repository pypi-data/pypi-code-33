from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="stem_feedback",
    version="0.5.12",
    author="Belyak",
    author_email="belyak.jul@gmail.com",
    description="Feedback package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.stemsc.com/Belyak_Yuliya/feedback",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'django>=1.11,<2',

    ]
)

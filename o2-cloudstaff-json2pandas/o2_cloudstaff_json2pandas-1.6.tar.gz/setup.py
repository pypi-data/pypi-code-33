import setuptools

setuptools.setup(
    name="o2_cloudstaff_json2pandas",
    version="1.6",
    author="Hudge",
    author_email="",
    description="",
    long_description="",
    long_description_content_type="text/markdown",
    url="",
    py_modules=["o2_cloudstaff_json2pandas"],
    install_requires=[
        "o2_docparser",
        "pandas",
        "openpyxl",
        "money2float",
        "o2_google_spreadsheet",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

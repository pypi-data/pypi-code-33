import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="o2_google_spreadsheet",
    version="0.1",
    author="Hudge",
    author_email="doug@mybusinessautomated.com",
    description="Google Spreadsheet helper file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/hudgeon",
    py_modules = ["o2_google_spreadsheet"],
    install_requires=[
        'requests',
        'pandas',
        'gspread',
        'oauth2client',
        'money2float'
    ],
    extras_require={
        '': '',
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
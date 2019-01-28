import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'flask_hmac_auth_m4l1c3',
    version = '1.0.7',
    description = 'A Flask middleware for HMAC request auth',
    author = 'm4l1c3',
    author_email = 'm4l1c3@tutanota.com',
    url = 'https://github.com/m4l1c3/flask-hmac-auth',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

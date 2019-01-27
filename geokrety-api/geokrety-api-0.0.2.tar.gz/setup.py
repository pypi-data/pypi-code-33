import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geokrety-api",
    version="0.0.2",
    author="Mathieu Alorent",
    author_email="kumy@geokrety.org",
    description="GeoKrety JSONAPI server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/geokrety/geokrety-api",
    packages=setuptools.find_packages(),
    install_requires=[
        "marshmallow-jsonapi==0.21.0",
        "gunicorn==19.9.0",
        "Flask-SQLAlchemy==2.3.2",
        "flask-cors==3.0.7",
        "Flask-OAuthlib==0.9.5",
        "flask-login==0.4.1",
        "wtforms==2.2.1",
        "envparse==0.2.0",
        "raven[flask]==6.10.0",
        "flask-jwt==0.3.2",
        "pytz==2018.9",
        "mysqlclient==1.4.1",
        "factory_boy==2.11.1",
        "bcrypt==3.1.6",
        "requests[security]==2.21.0",
        "flask-script==2.0.6",
        "characterentities==0.1.2",
        "geopy==1.18.1",
        "celery[redis]==4.2.1",
        "bleach==3.1.0",
        "pika-pool==0.1.3",
        "minio==4.0.10",
        "Flask-Minio==0.1.2",
        "geokrety-api-models==0.0.4",
    ],
    dependency_links=[
        "git+https://github.com/geokrety/flask-rest-jsonapi.git@geokrety2#egg=flask-rest-jsonapi",
        "git+https://github.com/geokrety/flask.git@issue-2900#egg=Flask&version=1.0.2",
        "git+https://github.com/exavolt/python-phpass.git#egg=python-phpass",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


import setuptools

setuptools.setup(
    name="sanic_templates",
    description="Templates support for the Python microframework Sanic",
    author="Jdraiv",
    version='1.0',
    url="https://github.com/jdraiv/sanic-templates",
    install_requires=[
        'jinja2',
        'sanic'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
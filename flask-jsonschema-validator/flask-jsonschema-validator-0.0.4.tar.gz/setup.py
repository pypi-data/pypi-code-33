import setuptools

with open( "README.md", "r" ) as fh:
    long_description = fh.read()

setuptools.setup(
    name = "flask-jsonschema-validator",
    version = "0.0.4",
    license = "MIT",
    author = "Daniel 'Vector' Kerr",
    author_email = "vector@vector.id.au",
    description = "Validate Flask JSON request data with schema files and route decorators",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    keywords = "flask jsonschema validator validation json schema",
    url = "https://gitlab.com/vector.kerr/flask-jsonschema-validator",
    packages = setuptools.find_packages(),
    install_requires = [ 'flask', 'jsonschema' ],
    classifiers = (
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)

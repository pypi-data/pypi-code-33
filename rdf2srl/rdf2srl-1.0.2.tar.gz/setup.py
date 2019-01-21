import pathlib
from setuptools import setup

# This directory
path = pathlib.Path(__file__).parent

readme_content = (path / "README.md").read_text()

setup(name="rdf2srl",
      version="1.0.2",
      description="Exposes RDF datasets from sparql endpoints for relational learning models in convenient formats",
      long_description=readme_content,
      long_description_content_type="text/markdown",
      url="https://github.com/aishahasmoh/RDF2SRL",
      author="Aisha Mohamed",
      author_email="ahmohamed@qcri.qf.org",
      classifiers=[
            "Programming Language :: Python :: 3.5",
      ],
      packages=["rdf2srl"],
      include_package_data=True,
      install_requires=["SPARQLWrapper", "pandas"],
      entry_points={},
      )

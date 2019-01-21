import pathlib

from setuptools import setup

path = pathlib.Path(__file__).parent

readme_content = (path / "README.md").read_text()

setup(name="rdf2srl",
      version="1.0.1",
      description="Exposes RDF datasets from sparql endpoints for relational learning models in convenient formats",
      long_description=readme_content,
      long_description_content_type="text/markdown",
      url="https://github.com/aishahasmoh/RDF2SRL",
      author="Aisha Mohamed",
      author_email="ahmohamed@qcri.qf.org",
      packages=["rdf2srl"],
      include_package_data=True,
      install_requires=["SPARQLWrapper", "pandas"],
      entry_points={},
      )

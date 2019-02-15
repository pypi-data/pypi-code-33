# Flit documentation build configuration file
# http://www.sphinx-doc.org/en/stable/config.html

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from fastgenomics import __version__


needs_sphinx = "1.3"

extensions = [
    "sphinx.ext.autodoc",  # API docs
    "sphinx.ext.napoleon",  # google-style docstrings
    "sphinx.ext.intersphinx",  # links to official docs
    "sphinx_autodoc_typehints",
]

intersphinx_mapping = dict(
    python=("https://docs.python.org/3", None),
    jsonschema=("https://python-jsonschema.readthedocs.io/en/v2.6.0/", None),
)

templates_path = ["_templates"]
exclude_patterns = ["_build"]
html_static_path = ["_static"]

source_suffix = ".rst"
master_doc = "index"

project = u"FASTGenomics"
copyright = u"2018, Comma Soft"

release = __version__
version = __version__  # short version

pygments_style = "sphinx"
html_theme = "sphinx_rtd_theme"
# html_theme_options = {}

# html_logo = '_static/flit_logo_nobg_cropped.svg'
# html_favicon = None

html_context = {
    "display_github": True,
    "github_user": "fastgenomics",
    "github_repo": "fastgenomics-py",
    "github_version": "master",
    "conf_py_path": "/doc/",
}

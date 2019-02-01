from setuptools import setup

if __name__ == "__main__":
    entry_points = {"sphinx.html_themes": ["bootstrap-limix = limix_sphinx_theme"]}
    setup(entry_points=entry_points)

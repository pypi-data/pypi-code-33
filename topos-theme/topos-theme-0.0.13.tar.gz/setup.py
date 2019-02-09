from setuptools import setup
from topos_theme import __version__


def readme():
    with open("README.rst") as f:
        return f.read()


setup(
    name="topos-theme",
    version=__version__,
    url="https://github.com/alcarney/topos-theme",
    license='MIT',
    author="Alex Carney",
    author_email="alcarneyme@gmail.com",
    description="Topos theme for sphinx",
    long_description=readme(),
    zip_safe=False,
    packages=['topos_theme'],
    package_data={'topos_theme': [
        "theme.conf",
        "*.html",
        "*.css"
    ]},
    include_package_data=True,
    # http://www.sphinx-doc.org/en/stable/theming.html#distribute-your-theme-as-a-python-package
    entry_points={
        "sphinx.html_themes": [
            "topos-theme = topos_theme"
        ]
    },
    install_requires=["sphinx"],
    classifiers=[
        'Framework :: Sphinx',
        'Framework :: Sphinx :: Theme',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
    ]
)

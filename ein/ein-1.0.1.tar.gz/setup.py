from setuptools import setup

long_description = """\
A placeholder for namespace package `ein`.

Thank [Reorx](https://pypi.org/user/Reorx/) for transfering this project on PyPI.org to me.
"""

setup(
    name="ein",
    version="1.0.1",
    description="namespace package for ein.plus",
    long_description=long_description,
    long_description_content_type="text/markdown",
    setup_requires=["setuptools>=38.6.0"],  # long_description_content_type support
    author="Qiangning Hong",
    author_email="hongqn@ein.plus",
    python_requires=">=3.3",  # for native namespace package
    packages=["ein.emptypackage"],
    extras_require={"dev": ["twine"]},
    zip_safe=False,
    license="MIT",
)

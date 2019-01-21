import pathlib
import re

from setuptools import setup


here = pathlib.Path(__file__).parent

txt = (here / "dspider" / "__init__.py").read_text("utf-8")
try:
    version = re.findall(r"""^__version__ = "([^']+)"\r?$""", txt, re.M)[0]
except IndexError:
    raise RuntimeError("Unable to determine version.")

long_description = "\n\n".join(
    [(here / "README.md").read_text("utf-8"), (here / "CHANGES.md").read_text("utf-8")]
)

install_requires = [
    "aiohttp>=3.5.4",
    "cssselect>=1.0.3",
    "jsonpath-rw>=1.4.0",
    "lxml>=4.3.0",
    "yarl>=1.3.0",
]


tests_require = ["pytest==4.0.1", "pytest-asyncio", "httpbin"]


setup(
    name="dspider",
    version=version,
    description="lightweight async crawler framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Topic :: Internet :: WWW/HTTP",
        "Framework :: AsyncIO",
    ],
    author="linw1995",
    author_email="linw1995@icloud.com",
    url="https://github.com/linw1995/dspider",
    project_urls={
        "GitHub: issues": "https://github.com/linw1995/dspider/issues",
        "GitHub: repo": "https://github.com/linw1995/dspider",
    },
    license="GPLv3",
    packages=["dspider"],
    python_requires=">=3.7",
    install_requires=install_requires,
    tests_require=tests_require,
)

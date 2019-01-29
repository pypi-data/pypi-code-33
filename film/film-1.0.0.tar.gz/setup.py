from setuptools import setup
from pathlib import Path


BASE = Path(__file__).parent
DESC = "Rename and organize movies"


def get_long_description() -> str:
    with open(BASE / "README.md", "r", encoding="utf-8") as f:
        return f.read()


setup(
    name="film",
    version="1.0.0",
    license="MIT",
    author="Dima Koskin",
    author_email="dmksknn@gmail.com",
    description=DESC,
    url="https://github.com/dmkskn/m",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
    py_modules=["movie"],
    install_requires=["isle"],
    entry_points={"console_scripts": ["film=movie:main"]},
)

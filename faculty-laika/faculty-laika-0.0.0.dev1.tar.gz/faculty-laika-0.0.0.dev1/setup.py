from setuptools import find_packages, setup


setup(
    name="faculty-laika",
    version="0.0.0.dev1",
    setup_requires=["setuptools_scm"],
    install_requires=[
        "tornado>=4.5,<5",
        "psutil",
        "requests",
        "python-dateutil",
        "jsonschema",
        "shellstorm>=0.2.4",
    ],
    python_requires='>=3.6',
)

from setuptools import find_packages, setup


setup(
    name="faculty-hound",
    version="0.0.0.dev0",
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
    entry_points={"console_scripts": ["hound=hound.app:run"]},
)

from setuptools import setup

pkgname = "semver-tool"
modname = pkgname.replace('-', '_')

setup(
    name=pkgname,
    use_scm_version={'write_to': 'src/__version__.py'},
    setup_requires=["setuptools_scm"],
    description="semantic version helper tool",
    long_description=open("README.md", "r").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Version Control",
    ],
    url="https://gitlab.com/aanatoly/semver-tool",
    author="Anatoly Asviyan",
    author_email="aanatoly@gmail.com",
    license="GPLv2",
    packages=['semver_tool'],
    package_dir={'semver_tool': 'src'},
    extras_require={"dev": ["tox", "cmarkgfm", "twine"]},
    entry_points={
        "console_scripts": [
            "%(pkgname)s = %(modname)s.__main__:main" % {"pkgname": pkgname, "modname": modname}
        ]
    },
    zip_safe=False,
)

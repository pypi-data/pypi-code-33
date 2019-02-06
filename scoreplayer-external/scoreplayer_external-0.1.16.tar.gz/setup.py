import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scoreplayer_external",
    version="0.1.16",
    author="Aaron Wyatt",
    author_email="python@psi-borg.org",
    description="Python external for controlling the Decibel ScorePlayer cavas mode",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://www.decibelnewmusic.com/decibel-scoreplayer.html",
    py_modules=["scoreplayer_external"],
    install_requires=["zeroconf", "python-osc"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Programming Language :: Python :: 3",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
    ],
)

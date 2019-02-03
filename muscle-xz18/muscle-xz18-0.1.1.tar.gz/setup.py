import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="muscle-xz18",
    version="0.1.1",
    author="xz18",
    description="weight lifting tracking app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/xz18/muscle",
    python_requires=">=3.5",
    packages=setuptools.find_packages(exclude=["test"]),
    test_suite="test",
    classifiers=[
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
    ],
    entry_points={
        'console_scripts': [
            'muscle = muscle.main:main'
        ]
    },
    project_urls={
        "Bug Report": "https://github.com/xz18/muscle/issues",
        "Source Code": "https://github.com/xz18/muscle"
    }
)

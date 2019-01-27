import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tabCompletion",
    version="1.0.0",
    author="Vaisakh Anand",
    author_email="vaisakh032@gmail.com",
    description="This package will help impart autocompletion to your python script inputs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/vaisakh032/tab-auto-completion",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
      install_requires=[
        'pynput>=1.4',
        'getch>=1.0'
    ],
)

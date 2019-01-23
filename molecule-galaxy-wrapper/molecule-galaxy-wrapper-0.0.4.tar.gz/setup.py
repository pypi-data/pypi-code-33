import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="molecule-galaxy-wrapper",
    version="0.0.4",
    author="Bernardo Vale",
    author_email="bernardosilveiravale@gmail.com",
    description="A wrapper for ansible-galaxy that allows you to define role dependencies inside a requirements.yml",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bernardoVale/molecule-galaxy-wrapper",
    keywords='molecule ansible ansible-galaxy galaxy dependency',
    packages=setuptools.find_packages(),
    install_requires=[
        'ruamel.yaml>=0.15.87',
    ],
    entry_points={
        'console_scripts': ['galaxywrapper=molecule_wrapper.cli:main'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)

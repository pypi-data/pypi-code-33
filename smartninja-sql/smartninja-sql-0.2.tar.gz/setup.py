import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='smartninja-sql',
    url='https://github.com/smartninja/smartninja-sql',
    author='Matej Ramuta',
    author_email='matej.ramuta@gmail.com',
    packages=['smartninja_sql'],
    install_requires=[],
    version='0.2',
    license='MIT',
    description='SmartNinja SQL - a simple SQLite wrapper.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

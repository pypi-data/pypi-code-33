import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='smartninja-mongo',
    url='https://github.com/smartninja/smartninja-mongo',
    author='Matej Ramuta',
    author_email='matej.ramuta@gmail.com',
    packages=['smartninja_mongo'],
    install_requires=["tinymongo", "pymongo"],
    version='0.3',
    license='MIT',
    description='SmartNinja Mongo - a simple MongoDB & TinyDB wrapper.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

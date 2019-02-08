import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-model-choices",
    version="1.0.0",
    author="Eerik Sven Puudist",
    author_email="eerik@herbfoods.eu",
    description="Django Model Choices provides a neat and DRY way to specify the `choices` option for a Django models and forms.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/eeriksp/django-model-choices",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
    ],
)
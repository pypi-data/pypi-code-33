import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="meapp",
    version="0.0.15",
    author="zhuxietong",
    author_email="zhuxietong@me.com",
    description="A small example packcage add tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/example-project",
    packages=setuptools.find_packages(),
    # packages=setuptools.find_packages(include=['core', 'location', 'tools','api']),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'django',
        'djangorestframework',
        'six',
        'Pillow',
        'aliyun-python-sdk-core-v3',
        'aliyun-python-sdk-ecs',
        # 'mysqlclient'
    ],
    include_package_data=True,
)

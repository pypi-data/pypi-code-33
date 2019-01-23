import setuptools

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


with open("README.rst", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="wakapy",
    version="0.0.1",
    author="surister",
    author_email="surister98@gmail.com",
    licesne='MIT',
    description="Wakatime data manipulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/surister/wakapy",
    include_package_data=True,
    python_requires='>3.6.0',
    install_requires=[
        'matplotlib'
    ],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet",
        "Topic :: Utilities"
    ],
)

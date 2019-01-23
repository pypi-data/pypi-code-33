import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ai_pipeline_params",
    version="0.0.2",
    author="Adrian Zhuang",
    author_email="wzhuang@us.ibm.com",
    description="Functions to set and use the AI Pipeline Params",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.ibm.com/AIOpsPipeline/kfp-samples/wml-containers",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'kfp',
        'kubernetes'
    ]
)

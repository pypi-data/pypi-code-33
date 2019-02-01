import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

package_name = 'magestore_aim'
packages = setuptools.find_packages(include=[package_name, "{}.*".format(package_name)])

setuptools.setup(
    name=package_name,
    version="1.2.4",
    author="Mars",
    author_email="mars@trueplus.vn",
    description="Auto install magento using docker",
    long_description=long_description,
    long_description_content_type="",
    url="https://github.com/Magestore/go-environment",
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3',
    install_requires=[
       'fabric'
    ]
)

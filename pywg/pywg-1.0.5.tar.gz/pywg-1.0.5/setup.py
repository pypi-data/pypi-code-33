from setuptools import setup, find_packages

setup(
    name = "pywg",
    version = "1.0.5",
    keywords = ("pip", "pywg"),
    description = "A machine learning frame.",
    long_description = "A machine learning frame.",
    author = "wg",
    url = "https://gitee.com/hk_wg/projects",
    author_email = "2654764580@qq.com",
    license = "MIT",
    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["numpy","matplotlib"]
)

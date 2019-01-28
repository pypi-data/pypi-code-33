from setuptools import setup, find_packages

setup(
    name="labulac",
    version="0.2.1",
    keywords=("pip", "labulac", "labula"),
    description="firs tool",
    long_description="软件源",
    license="MIT Licence",
    url="https://github.com/labulac/labulac",
    author="cms",
    author_email="740162752@qq.com",
    packages=["LABULAC"],
    include_package_data=True,
    platforms="any",
    zip_safe=True,
    install_requires=[
        'docopt',
    ],
    entry_points={'console_scripts': ['labulac = LABULAC.labulac:main']},
)

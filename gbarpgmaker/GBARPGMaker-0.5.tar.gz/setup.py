import setuptools

setuptools.setup(
    name="GBARPGMaker",
    version="0.5",
    description="a program that helps with development of GBA games",
    packages=setuptools.find_packages(),
    url="https://gitlab.com/kockahonza/gbarpgmaker",
    package_data={'': ['*.c', '*.h']},
    include_package_data=True,
    install_requires=["jinja2", "pillow"],
)

import setuptools

setuptools.setup(
    name="plugwise", 
    version="0.7",
    description="A library for communicating with Plugwise smartplugs",
    author="Sven Petai",
    author_email="hadara@bsd.ee",
    url="https://github.com/cyberjunky/plugwise",
    license="MIT",
    packages=setuptools.find_packages(),
    py_modules=["plugwise"],
    install_requires=[
       'pyserial',
    ],
    scripts=["plugwise_util"],
)

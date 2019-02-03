from setuptools import setup
import os 

def read(fname):
    return open(os.path.join(os.path.dirname(__file__),fname)).read()

setup(

    name = "nesterkunwar",
    version = "1.2.0",
    py_modules = ["nesterkunwar"],
    author = "Kunwar Shamsher Luthera",
    author_email = "kunwarluthera@gmail.com",
    url = "https://github.com/kunwarluthera/nesterkunwar",
    description = "This is first module for nested lines",
    long_description=read('README')

)
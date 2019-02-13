import os
from Cython.Build import cythonize
from setuptools import setup, Extension, find_packages


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


SRC_DIR = "math_round_source"
REQUIRES = ['cython']

ext = Extension(name=SRC_DIR + '.c_math_round', sources=[SRC_DIR + "/c_math_round.pyx"])
if __name__ == "__main__":
    setup(
        name='math-round',
        version='0.0.1',
        description='Mathematical rounding for python 3',
        url='https://github.com/anisov/math-round',
        long_description=read('README.rst'),
        packages=find_packages(),
        license="MIT",
        author='Anisov Dmitriy',
        author_email='dimaanisov24@gmail.com',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
        keywords=['math', 'round', 'math-round'],
        ext_modules=cythonize(ext),
        install_requires=REQUIRES,
    )

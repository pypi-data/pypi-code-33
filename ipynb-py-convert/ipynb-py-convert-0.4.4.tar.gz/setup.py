from setuptools import setup
from os import path
import io

here = path.abspath(path.dirname(__file__))
with io.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ipynb-py-convert',
    packages=['ipynb_py_convert'],
    version='0.4.4',
    description='Convert .py files runnable in VSCode/Python or Atom/Hydrogen to jupyter .ipynb notebooks and vice versa',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Noj Vek',
    author_email='nojvek@gmail.com',
    license='MIT',
    url='https://github.com/kiwi0fruit/ipynb-py-convert',
    keywords=['vscode', 'jupyter', 'convert', 'ipynb', 'py', 'atom', 'hydrogen'],
    classifiers=[],
    entry_points={
        'console_scripts': [
            'ipynb-py-convert=ipynb_py_convert.__main__:main',
        ],
    },
)

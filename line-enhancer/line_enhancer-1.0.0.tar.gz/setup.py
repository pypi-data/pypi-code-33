from setuptools import setup
# Create new package with python setup.py sdist
setup(
    name='line_enhancer',
    version='1.0.0',

    packages=['line_enhancer'],
    url='',
    license='MIT',
    author='Thorsten Wagner',
    install_requires=[
        "numpy >= 1.13.3",
        "mrcfile",
        "scipy"
    ],
    author_email='thorsten.wagner@mpi-dortmund.mpg.de',
    description='Enhancing line images',
    entry_points={
        'console_scripts': [
            'line_enhance.py = line_enhancer.line_enhancer:_main_']},
)
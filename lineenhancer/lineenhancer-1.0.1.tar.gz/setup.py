from setuptools import setup
# Create new package with python setup.py sdist
setup(
    name='lineenhancer',
    version='1.0.1',

    packages=['lineenhancer'],
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
            'line_enhancer.py = lineenhancer.line_enhancer:_main_']},
)
from setuptools import setup




setup(
    name='PatternTuring',
    version='0.2',
    description='simulation of Turing Pattern',
    url='https://github.com/tsuchiura/kadai',
    author='tsuchiura',
    author_email='tsuchiurax@gmail.com',
    license='MIT',
    keywords='turing pattern simulation',
    packages=[
        "PatternTuring",
    ],
    install_requires=[
        "numpy",
        "matplotlib",
    ],
    classifiers=[
        'Programming Language :: Python :: 3.6',
    ],
)


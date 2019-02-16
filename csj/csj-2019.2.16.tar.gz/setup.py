from setuptools import setup

with open('README.md', 'r') as readme:
    readme = "".join(readme.readlines())

setup(
    name='csj',
    version='2019.2.16',
    url='https://github.com/bartbroere/csj/',
    author='Bart Broere',
    author_email='mail@bartbroere.eu',
    license='MIT License',
    description="Read comma separated JSON",
    keywords='csj csv json',
    long_description=readme,
    py_modules=['csj'],
    classifiers=(
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Utilities',
    )
)

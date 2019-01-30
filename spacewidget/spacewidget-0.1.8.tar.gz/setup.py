import setuptools

setuptools.setup(
    name='spacewidget',
    version='0.1.8',
    author='foosinn',
    author_email='foosinn@f2o.io',
    url='https://github.com/foosinn/spacewidget',
    license="AGPL 3.0",
    install_requires=[
        'aiohttp',
    ],
    packages=setuptools.find_packages(),
    package_data={
        'spacewidget': ['index.html'],
    },
    entry_points={
        'console_scripts': [
            'spacewidget=spacewidget.widget:main',
        ],
    },
)

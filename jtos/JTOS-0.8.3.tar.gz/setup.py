import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'JTOS',
    version = '0.8.3',
    description = 'A JSON query to SQL parser loosely based on the Loopback Query Language',
    long_description = long_description,
    url ="https://github.com/encima/jtos",
    author = 'encima',
    author_email = 'encima@gmail.com',
    classifiers = [
	'Development Status :: 3 - Alpha',
	'Intended Audience :: Developers',
	'Topic :: Software Development',
    'Topic :: Database',
	'License :: OSI Approved :: MIT License',
	'Programming Language :: Python :: 2',
	'Programming Language :: Python :: 2.6',
	'Programming Language :: Python :: 2.7',
	'Programming Language :: Python :: 3',
    ],
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
)


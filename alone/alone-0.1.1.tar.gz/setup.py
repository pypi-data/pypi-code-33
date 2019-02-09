import setuptools


setuptools.setup(
    name='alone',
    version='0.1.1',
    author_email='adrien.pierre.horgnies@gmail.com',
    description='Metaclass that defines a class as a singleton',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/AdrienHorgnies/py-singleton',
    packages=setuptools.find_packages(),
    install_requires=[],
    license='MIT License',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers'
    ],
    keywords=['singleton']
)

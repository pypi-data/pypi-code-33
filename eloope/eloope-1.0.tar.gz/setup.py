import setuptools

setuptools.setup(
    name='eloope',
    version='1.0',
    author='Czw_96',
    author_email='459749926@qq.com',
    description='Distributed event loop engine.',
    url='https://github.com/Czw96/eloope',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': ['eloope = eloope.command:main']
    }
)

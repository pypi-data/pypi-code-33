import setuptools

setuptools.setup(
    name='propor',
    version='1.3',
    author='Czw_96',
    author_email='459749926@qq.com',
    description='Project porter.',
    url='https://github.com/Czw96/propor',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts': ['propor = propor.main:main']
    },
    install_requires=[
        'paramiko',
    ]
)

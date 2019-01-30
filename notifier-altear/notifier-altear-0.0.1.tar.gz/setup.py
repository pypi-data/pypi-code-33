import setuptools

setuptools.setup(
    name="notifier-altear",
    version="0.0.1",
    author="Andre Telfer",
    author_email="andretelfer@gmail.com",
    description="A small package for sending notification emails",
    install_requires=[
        "click >= 7.0"
    ],
    packages=[
        'notifier',
        ''
    ],
    entry_points={
        'console_scripts': [
            'notify=notifier.main:cli',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['README.md', 'LICENSE', 'MANIFEST.in'],
        'notifier': ['resources/*.json']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
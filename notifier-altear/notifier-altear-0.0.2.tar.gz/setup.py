import setuptools

with open('README.md', 'r') as fp:
    long_description = fp.read()

setuptools.setup(
    name="notifier-altear",
    version="0.0.2",
    author="Andre Telfer",
    author_email="andretelfer@gmail.com",
    description="A small package for sending notification emails",
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        "click"
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
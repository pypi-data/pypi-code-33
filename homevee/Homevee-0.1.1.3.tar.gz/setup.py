import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Homevee",
    version="0.1.1.3",
    author="Homevee",
    author_email="support@homevee.de",
    description="Dein neues Smarthome-System!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/homevee/homevee",
    entry_points = {
        'console_scripts': ['homevee=homevee.command_line:main'],
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'python-dateutil',
        'pyOpenSSL',
        'tensorflow',
        'tensorflow-gpu',
        'pymax',
        'paho-mqtt',
        'Pillow',
    ]
)

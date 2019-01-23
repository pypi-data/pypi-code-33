import setuptools

setuptools.setup(
    name='pycoap',
    version='0.0.7',
    packages=['pycoap','pycoap.packet'],
    license='MIT License',
    author="Eric Wilkison",
    author_email="ericw@wilkison.com",
    long_description=open('README.txt').read(),
    url='https://bitbucket.org/ericwilkison/pycoap',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

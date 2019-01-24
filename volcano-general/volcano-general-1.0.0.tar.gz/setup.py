from setuptools import setup
import json

with open('info.json') as f:
    info = json.load(f)

setup(
    name='volcano-general',
    version=info['version'],
    description='Volcano basic utilities',
    author='Vinogradov D',
    author_email='dgrapes@gmail.com',
    license='MIT',
    packages=['volcano.general'],
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)

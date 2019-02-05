from setuptools import setup
import setuptools


def readme():
    with open('README.md') as f:
        README = f.read()
    return README


setup(
    name="insta-scraper",
    version="1.1.1",
    description="A python tool to download instagram users media.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    author="Naveen Tummidi",
    author_email="naveentummidi0807@gmail.com",
    classifiers=[
            'Topic :: Software Development :: Libraries',
            'Operating System :: OS Independent',
            'Development Status :: 5 - Production/Stable',
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 2.7",
    ],
    license="MIT",
    keywords='instagram instagram-scraper',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["requests", "bs4", "wget", "argparse"],
    entry_points={
        "console_scripts": [
            "insta-scraper=insta.insta:main",
        ]
    },
    project_urls={
        'Funding': 'https://donate.pypi.org',
    },
)

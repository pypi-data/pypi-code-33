from setuptools import setup, find_packages
from pingstats import __version__

# with open("README.rst", "r") as fh:
#     long_description = fh.read()

with open("requirements.txt", "r") as f:
    required = f.read().splitlines()

setup(
    name='pingstats',
    version=__version__,
    description='Simple ping visualization on the CLI',
    # long_description=long_description,
    # long_description_content_type="text/x-rst",
    url='http://gitlab.com/eclectickmediasolutions/pingstats',
    author='Ariana Giroux',
    author_email='ariana.giroux@gmail.com',
    license='MIT',
    packages=find_packages(),
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    install_requires=required,
    zip_safe=True,
    entry_points={
        'console_scripts': ['pingstats=pingstats.ui:_run'],
    },
    classifiers=(
                "Programming Language :: Python :: 3",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
                "Development Status :: 4 - Beta",
                "Environment :: Console",
                "Intended Audience :: Developers",
                "Intended Audience :: End Users/Desktop",
                "Intended Audience :: Information Technology",
                "License :: OSI Approved :: MIT License",
                "Operating System :: Unix",
                "Topic :: System :: Networking :: Monitoring",
                "Topic :: Utilities",
    ),
)

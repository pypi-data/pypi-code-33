from setuptools import setup, find_packages

setup(
    name='VOEventLib',
    version='1.2',
    author='Roy D. Williams',
    author_email='roy.williams@ligo.org',
    maintainer='Min-A Cho',
    maintainer_email='min-a.cho@ligo.org',
    license='GNU General Public License Version 3',
    description='Python library to read, modify, and create VOEvents',
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Internet",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics"
    ),
    packages=find_packages(),
    python_requires='>=3.5',
)

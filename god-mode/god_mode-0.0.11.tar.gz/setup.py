try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

REQUIRED_PACKAGES = [
    'pyAesCrypt==0.4.2',
    'colorama==0.4.1',
    'PyYAML==3.13'
]

setup(
    name="god_mode",
    version="0.0.11",
    author="Nicolas Lettiere",
    author_email="braum.exe@gmail.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=REQUIRED_PACKAGES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        'console_scripts': [
            'crypt = god_mode.crypt:main'
        ],
    }
)
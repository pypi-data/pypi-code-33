import setuptools
from setuptools.command.build_py import build_py
from wheel.bdist_wheel import bdist_wheel 

class BDistWheel(bdist_wheel):
    def finalize_options(self):                
        bdist_wheel.finalize_options(self)
        self.root_is_pure=False

    def get_tag(self):
        python, abi, plat = bdist_wheel.get_tag(self)
        plat=plat.replace('linux','manylinux1')
        return python, abi, plat

with open("README.rst","r") as h:
    long_description=h.read()

setuptools.setup(
    cmdclass={
        'bdist_wheel': BDistWheel
    },
    name="scanimage-tiff-reader",
    version="1.4",
    author="Nathan Clack",
    author_email="nathan@vidriotech.com",
    description="A fast (big)tiff reader that provides access to ScanImage-specific metadata.",
    url="https://gitlab.com/vidriotech/scanimagetiffreader-python",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    package_dir={'':'src'},
    packages=["ScanImageTiffReader"],
    include_package_data=True,
    setup_requires=['pytest-runner'],
    tests_require=['pytest','numpy'],
    install_requires=["numpy"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: MacOS :: MacOS X",
        "Environment :: MacOS X",
        "Environment :: Win32 (MS Windows)",
        "Topic :: Scientific/Engineering",
        "Development Status :: 5 - Production/Stable"
    ],
)

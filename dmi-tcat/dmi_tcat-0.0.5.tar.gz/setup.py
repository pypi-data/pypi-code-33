import setuptools

with open("README.md", 'r') as fh:
    long_description = fh.read()

setuptools.setup(name='dmi_tcat',
                 version='0.0.5',
                 author="Mace Ojala",
                 author_email="mace.ojala@gmail.com",
                 description="A little Python interface to DMI TCAT",
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url="https://github.com/xmacex/dmi_tcat",
                 packages=setuptools.find_packages(),
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                     "Operating System :: OS Independent",
                     ]
                 )

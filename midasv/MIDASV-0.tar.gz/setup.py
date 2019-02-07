import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='MIDASV',
      version='0',
      description='MIDAS is a system for generating Boolean Framework for Modeling and Inferring Drug Targets and Drug Resistance Mechanisms',
      author='Vrushali Dipak Fangal, Amitabh Sharma, Channing Division of Network Medicine, Harvard Medical School',
      author_email='vrushali@broadinstitute.org',
      url='https://github.com/vrushali-broad/MIDAS/tree/master',
      long_description=long_description,
      long_description_content_type="text/markdown",
      packages=setuptools.find_packages(),
      classifiers=[
       "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
  

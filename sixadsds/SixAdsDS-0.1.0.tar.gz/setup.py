import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SixAdsDS",
    version="0.1.0",
    author="Eligijus Bujokas",
    author_email="eligijus@sixads.net",
    description="Generic functions for SixAds data science projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/eligijus112/sixadsml/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires = [ 
        'inflection',
        'nltk', 
        'pandas',
        'sqlalchemy',
        'PyYAML', 
        'keras', 
        'tensorflow', 
        'sklearn', 
        'tqdm', 
        'pymysql', 
        'opencv-python'            
            ]        
)  

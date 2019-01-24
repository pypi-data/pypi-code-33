import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dominance_analysis",
    version="1.0.3",
    author="Sajan Kumar Bhagat, Kunjithapatham Sivakumar, Shashank Shekhar",
    author_email='bhagat.sajan0073@gmail.com, s.vibish@gmail.com, quintshekhar@gmail.com',
    maintainer="Sajan Kumar Bhagat, Kunjithapatham Sivakumar, Shashank Shekhar",
    maintainer_email='bhagat.sajan0073@gmail.com, s.vibish@gmail.com, quintshekhar@gmail.com',
    description='Dominance Analysis',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/bhagatsajan0073/dominance_analysis',
    packages=setuptools.find_packages(),
    license='MIT',
    zip_safe=False,
    classifiers=[
        # "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=["Dominance Analysis","Feature Importance","Feature Selection"],
    install_requires=[
          'pandas==0.23.4',
          'numpy==1.15.4',
          'seaborn==0.9.0',
          'matplotlib==2.2.2',
          'scikit-learn==0.19.1',
          'tqdm==4.28.1',
          'plotly==2.5.0',
          'cufflinks==0.12.1',
          'statsmodels==0.9.0',
          'ipywidgets==5.2.2'
    ],
    include_package_data=True
)
from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='sigproextractor',
      version='0.0.5.6',
      description='Extracts mutational signatures from mutational catalogues',
      url="https://github.com/AlexandrovLab/SigProfilerExtractor.git",
      author='S Mishu Ashiqul Islam',
      author_email='m0islam@ucsd.edu',
      license='UCSD',
      packages=['sigproextractor'],
      install_requires=[
          'matplotlib==2.2.2',
          'scipy==1.1.0', 
          'numpy==1.14.3', 
          'pandas==0.23.4', 
          'nimfa==1.1.0', 
          'SigProfilerMatrixGenerator==0.1.20', 
          'sigProfilerPlotting==0.1.17', 
          'pillow',
          'statmodels==0.9.0'
           ],
      include_package_data=True,      
      zip_safe=False)

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='sigproextractor',
      version='0.0.5.2',
      description='Extracts mutational signatures from mutational catalogues',
      url="https://github.com/AlexandrovLab/SigProfilerExtractor.git",
      author='S Mishu Ashiqul Islam',
      author_email='m0islam@ucsd.edu',
      license='UCSD',
      packages=['sigproextractor'],
      install_requires=[
          'matplotlib','scipy', 'numpy', 'pandas', 'nimfa', 'SigProfilerMatrixGenerator', 'sigProfilerPlotting'
      ],
      include_package_data=True,      
      zip_safe=False)

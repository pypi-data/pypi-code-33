from setuptools import setup



setup(name='sigproSS',
      version='0.0.0.11',
      description=' Decomposes mutational catalogues to mutational signatures',
      url="https://github.com/AlexandrovLab/SigProfilerExtractor.git",
      author='S Mishu Ashiqul Islam',
      author_email='m0islam@ucsd.edu',
      license='UCSD',
      packages=['sigproSS'],
      install_requires=[
          'matplotlib>=2.2.2',
	  'scipy>=1.1.0', 
	  'numpy>=1.14.4', 
	  'pandas>=0.23.4', 
	  'SigProfilerMatrixGenerator>=0.1.20', 
	  'sigProfilerPlotting>=0.1.17', 
	  'sigproextractor>=0.0.5.6', 
	  'statsmodels>=0.9.0'
      	   ],
      include_package_data=True,      
      zip_safe=False)

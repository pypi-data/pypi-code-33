from setuptools import setup



setup(name='sigproSS',
      version='0.0.0.6',
      description=' Decomposes mutational catalogues to mutational signatures',
      url="https://github.com/AlexandrovLab/SigProfilerExtractor.git",
      author='S Mishu Ashiqul Islam',
      author_email='m0islam@ucsd.edu',
      license='UCSD',
      packages=['sigproSS'],
      install_requires=[
          'matplotlib','scipy', 'numpy', 'pandas', 'SigProfilerMatrixGenerator', 'sigProfilerPlotting', 'sigproextractor'
      ],
      include_package_data=True,      
      zip_safe=False)

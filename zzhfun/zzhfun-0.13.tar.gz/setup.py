import setuptools
setuptools.setup(name='zzhfun',
      version='0.13',
      description='zzh model function and data function',
      url='https://github.com/FlashSnail/zzhfun',
      author='Zzh',
      author_email='zzh_0729@foxmail.com',
      packages=setuptools.find_packages(),
      classifiers=[
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ],
      install_requires=[
        'pandas>=0.20.3',
        'numpy>=1.14.2',
        'xgboost>=0.72.1',
        'keras>=2.2.4',
        'scikit-learn>=0.20.0',
      ]      
      )

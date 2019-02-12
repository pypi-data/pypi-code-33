from setuptools import setup, find_packages


version = '0.2'


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='aeropy',
      version=version,
      python_requires='>=3',
      description='A universal aerospace engineering toolbox',
      long_description=readme(),
      long_description_content_type="text/markdown",
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
      ],
      keywords='aerospace engineering airfoils noise aircraft',
      url='https://bitbucket.org/lukas-mueller/aeropy',
      download_url='https://bitbucket.org/lukas-mueller/aeropy/raw/master/dist/aeropy-'+version+'.tar.gz',
      author='Lukas Mueller',
      author_email='lukas.mueller94@gmail.com',
      license='MIT License',
      packages=find_packages(),
      install_requires=[
            'matplotlib',
            'numpy',
            'pandas',
            'scipy'
      ],
      include_package_data=True,
      zip_safe=False)

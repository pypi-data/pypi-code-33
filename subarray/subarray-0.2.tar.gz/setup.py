import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(name='subarray',
      version='0.2',
      description='get 2D sub array slices from a large 2D array',
      author='Tasin Nawaz',
      author_email='tasin.buet@gmail.com',
      license='TN',
      url='https://github.com/tasin-megamind/subarray',
      long_description=long_description,
      long_description_content_type='text/markdown',
      packages=setuptools.find_packages(),
      include_package_data=True,
      install_requires=[
      ],
      zip_safe=False)


import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='NowTCP',
    version='0.0.4',
    author='truedl',
    author_email='dauzduz1@gmail.com',
    description='🌀 NowTCP - Fast create your TCP Server/Client 🌀',
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/truedl/NowTCP',
    packages=setuptools.find_packages(),
 )
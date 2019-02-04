from setuptools import setup
import setuptools

setup(
    name='forceclient',
    packages=setuptools.find_packages(),
    version='0.1',
    description='Python wrapper for the ForceManager API',
    license='MIT',
    author='Bjarni Juliusson',
    author_email='bjarni@stilling.is',
    url='https://github.com/bingimar/ForceClient',
    download_url='https://github.com/bingimar/ForceClient.git',
    install_requires=[
        'requests==2.21.0',
    ],
    keywords=['forcemanager', 'api', 'wrapper'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'License :: OSI Approved :: MIT License'
    ],
)

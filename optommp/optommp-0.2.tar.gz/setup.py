from setuptools import setup

setup(name='optommp',
        version='0.2',
        description='Python toolkit for Opto 22 memory-mapped devices',
        long_description="Python toolkit to access data on Opto 22 *groov* EPIC. See developer.opto22.com and OptoMMP Protocol Guide for more details: https://www.opto22.com/support/resources-tools/documents/1465-optommp-protocol-guide (form 1465).",
        url='http://github.com/optodeveloper/optommp',
        download_url='https://github.com/optodeveloper/optommp/archive/v0.2.tar.gz',
        license='mit',
        author='Opto 22',
        author_email='torchard@opto22.com',
        packages=['optommp'],
        zip_safe=False,
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2.7'
            ])

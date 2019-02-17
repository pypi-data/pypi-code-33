from setuptools import (setup, find_packages)

setup(
    name='image_file_name_fixer',
    version='0.10.1',
    description='Image File Name Fixer',
    author='Jeremy Reed',
    author_email='reeje76@gmail.com',
    license='MIT',
    url='https://gitlab.com/jeremymreed/image-file-name-fixer',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['image-file-name-fixer=image_file_name_fixer.__main__:main']
    }
)

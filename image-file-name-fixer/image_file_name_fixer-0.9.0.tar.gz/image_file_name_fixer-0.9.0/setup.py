from setuptools import setup

setup(
    name='image_file_name_fixer',
    version='0.9.0',
    description='Image File Name Fixer',
    author='Jeremy Reed',
    author_email='reeje76@gmail.com',
    license='MIT',
    url='https://gitlab.com/jeremymreed/image-file-name-fixer',
    entry_points={
        'console_scripts': ['image-file-name-fixer=image_file_name_fixer.__main__:main']
    }
)

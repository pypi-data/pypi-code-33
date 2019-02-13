from setuptools import setup, find_packages
import sys

setup(
    name='sortvis',
    version='1.0.0',
    keywords = ("sort", "method", "visual", "visualization"),
    description='Visualized sorting method',
    license='MIT',
    author='frank-xjh',
    author_email='frank99-xu@outlook.com',
    url='https://github.com/frank-xjh/Sort-Visualization',
    packages=find_packages(),
    include_package_data = True,
    install_requires = ["numpy", "opencv-python"],
    entry_points={
        'console_scripts': [
            'sortvis=__main__:main'
        ]
    }
)
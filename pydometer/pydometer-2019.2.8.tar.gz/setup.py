from setuptools import setup, find_packages

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setup(
    name='pydometer',
    version='2019.02.08',
    description='Python functions to count steps in accelerometer data',
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url='https://bitbucket.org/atpage/pydometer',
    author='Alex Page',
    author_email='alex.page@rochester.edu',
    # classifiers=[
    #     'License :: OSI Approved :: MIT License',
    #     'Programming Language :: Python :: 3',
    #     "Operating System :: OS Independent",
    # ],
    python_requires='>=3.0',
    packages=find_packages(exclude=['tests']),
    install_requires=['numpy', 'scipy', 'pandas'],
    keywords='pedometer accelerometer steps',
    package_data={
        'pydometer': ['example_data/*.bin'],
    },
    #zip_safe=False
)

from setuptools import setup

setup(name='morestd',
      version='0.3',
      description='A collection of additional standard libraries for Python.',
      long_description=open('README.md').read(),
      long_description_content_type="text/markdown",
      url='https://github.com/fboender/morestd',
      author='Ferry Boender',
      author_email='ferry.boender@gmail.com',
      license='MIT',
      packages=['morestd'],
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      zip_safe=True)

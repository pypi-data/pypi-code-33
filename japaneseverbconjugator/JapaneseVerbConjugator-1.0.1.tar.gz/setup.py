import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='JapaneseVerbConjugator',
    version='1.0.1',
    author='Jacob Shiohira',
    author_email='shiohira.jacob@gmail.com',
    description='Japanese verb Conjugator',
    long_description=long_description,
    url='https://github.com/jShiohaha/JapaneseVerbConjugator/',
    packages=setuptools.find_packages(),
    install_requires=[
          'romkan',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
    ],
)
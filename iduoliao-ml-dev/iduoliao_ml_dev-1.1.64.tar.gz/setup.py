import setuptools, shutil

try:
    shutil.rmtree('build')
    shutil.rmtree('dist')
    shutil.rmtree('iduoliao_ml.egg-info')
except Exception as error:
    print('Error: ' + str(error))

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iduoliao_ml_dev",
    version="1.1.64",
    author="legend",
    author_email="huangzhen@gzecy.com",
    description="iduoliao machine learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    #packages=['iduoliao_ml', 'iduoliao_ml.data', 'iduoliao_ml.es', 'iduoliao_ml.ilog',  'iduoliao_ml.imatrix',  'iduoliao_ml.recommend'],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
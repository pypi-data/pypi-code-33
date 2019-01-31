from setuptools import setup

readme = open('README.md').read()

setup(
    name="stcorr",
    version="0.0.0",
    description="Spatial and Temporal Correlation Analysis",
    author="Jun Ke, Xuefei Cao, Xi Luo",
    packages=['stcorr'],
    long_description=readme,
    long_description_content_type='text/markdown',
    install_requires=[
        "numpy>=1.11.1",
        "scipy>=0.19.0",
    ],
    url='https://github.com/xuefeicao/stc',
    include_package_data=True,
    )

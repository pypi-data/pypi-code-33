from setuptools import setup

with open("README.md", "r", encoding='UTF-8') as fh:
    long_description = fh.read()

setup(
    name='scatter3d',
    version='0.2',
    package_dir={'scatter3d': 'src'},
    packages=['scatter3d'],
    package_data={'': ['*.html', '*.js']},
    author='wcy',
    author_email='1208640961@qq.com',
    description='结合flask生成3d散点模型,并在浏览器中浏览',
    long_description=long_description,
    long_description_content_type="text/markdown",
)

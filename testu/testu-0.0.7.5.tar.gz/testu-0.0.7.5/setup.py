from setuptools import setup

with open('README.md') as f:
    long_description = f.read().split("## User permissions")[0]

setup(
    author='dairoot',
    author_email='623815825@qq.com',
    description='A PyPI package with a Markdown README',
    long_description=long_description,
    long_description_content_type='text/markdown',  # This is important!
    name='testu',
    url='http://github.com/di/markdown-description-example',
    version='0.0.7.5',
    data_files=["README.md"],
)

from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gorep',
    version='0.1.1',
    description='Gor Grep Middleware.',
    long_description=long_description,
    long_description_content_type='text/markdown',

    author='ycyuxin',
    author_email='ycyuxin@qq.com',
    url='https://github.com/huyx/gorep',

    scripts=['gorep.py'],
    entry_points='''
    [console_scripts]
    gorep=gorep:cli
    '''
)

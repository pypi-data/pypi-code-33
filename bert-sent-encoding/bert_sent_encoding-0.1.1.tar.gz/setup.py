from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
	long_description = f.read()

setup(
	name='bert_sent_encoding',
	version='0.1.1',
	description='A bert sentence encoding tool',
	long_description=long_description,
	long_description_content_type='text/markdown',
	license='BSD',
	url='https://gitlab.leihuo.netease.com/shaojianzhi/bert-sent-encoding',
	author='Shao Jianzhi',
	author_email='shaojianzhi2012@163.com',
	packages=['bert_sent_encoding'],
	install_requires=['tqdm', 'boto3', 'botocore', 'requests', 'numpy', 'torch'],
	include_package_data=True,
)

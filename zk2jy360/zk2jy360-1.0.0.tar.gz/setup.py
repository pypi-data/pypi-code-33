# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
	# 以下为必需参数
	name='zk2jy360',  # 模块名
	version='1.0.0',  # 当前版本
	description='This is the module of ZK attendance machine submitting attendance data to Jianyan360.',  # 简短描述
	py_modules=["zk2jy360"], # 单文件模块写法
	# ckages=find_packages(exclude=['Tests']),  # 多文件模块写法


	# 以下均为可选参数
	long_description="",# 长描述
	url='http://www.jianyan360.com', # 主页链接
	author='Zhouyun', # 作者名
	author_email='251920948@qq.com', # 作者邮箱
	classifiers=[
		'Development Status :: 3 - Alpha',  # 当前开发进度等级（测试版，正式版等）

		'Intended Audience :: Developers', # 模块适用人群
		'Topic :: Software Development :: Build Tools', # 给模块加话题标签

		'License :: OSI Approved :: MIT License', # 模块的license

		'Programming Language :: Python :: 2.7',
	],
	keywords='ZK jianyan360',  # 模块的关键词，使用空格分割
	install_requires=['requests'], # 依赖模块
	# extras_require={  # 分组依赖模块，可使用pip install sampleproject[dev] 安装分组内的依赖
	# 	'dev': ['check-manifest'],
	# 	'test': ['coverage'],
	# },
	packages = ['Tests'],
	# package_data={  # 模块所需的额外文件
	# 	'': ['*.md']
	# }, 
	# data_files=[('', ['*.md'])], # 类似package_data, 但指定不在当前包目录下的文件
	entry_points={  # 新建终端命令并链接到模块函数
		# 'console_scripts': [
		# 	'zk2jy360=zk2jy360:version',   
		# ],
	},
	# project_urls={  # 项目相关的额外链接
	# 	'Bug Reports': 'http://www.jianyan360.com',
	# 	'Funding': 'https://donate.pypi.org',
	# 	'Say Thanks!': 'http://www.jianyan360.com',
	# 	'Source': 'http://www.jianyan360.com',
	# },
)
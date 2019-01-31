# -*- coding: utf-8 -*-
import setuptools

with open("README.md", encoding="utf8") as f:
    long_description = f.read()
#编写配置文件让python进行读取，获取到里面的version的版本号
with open("version.txt",encoding="utf8") as v:
    version = v.read()

setuptools.setup(name="lznlp",
                 version=version,
                 author="liangzhi",
                 author_email="service@quant-chi.com",
                 description="LiangZhiNLP API wrapper",
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 url="http://192.168.1.26:8099/liangzhi.ai/lznlp-platform/tree/master/scripts/lznlp.sdk",
                 packages=setuptools.find_packages(),
                 license="MIT",
                 classifiers=[
                     'Development Status :: 5 - Production/Stable',
                     'Intended Audience :: Developers',
                     'Operating System :: OS Independent',
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     'Topic :: Software Development :: Libraries :: Python Modules',
                     'Topic :: Software Development :: Testing',
                 ],
                 install_requires=[
                     "requests>=2.0.0",
                     "nose",
                     "keras",
                     #"fasttext",
                     "xgboost",
                     "pika",
                     "scrapy",
                     "w3lib",
                     "lxml"
                 ],
                 include_package_data=True,
                 zip_safe=False,
                 )

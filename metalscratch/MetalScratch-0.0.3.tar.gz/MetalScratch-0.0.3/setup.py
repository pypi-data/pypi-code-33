# coding=utf-8

from setuptools import setup, find_packages


setup(
    name='MetalScratch',  # '库的名称,一般写成文件夹的名字就可以了，也有的人不写成文件夹的名字，那么pip install和具体的import使用时候就不一样了，用起来会十分蛋疼，有一些包就是这样的。比如一个包，安装时候是pip install  xxx,但当你要使用时候要import yyy


    version="0.0.3",                  # 版本，每次发版本都不能重复，每次发版必须改这个地方
    description=(
        'A Python-based library for Scratch functionality'   # 一个简介，别人搜索包时候，这个概要信息会显示在在搜索列表中

    ),
    author='Metal_Studio',       # 作者
    author_email='metal_studio@foxmail.com',
    license='MIT License',
    # packages=['douban'], # 发布的包名
    packages=find_packages(),
    platforms=["all"],
    url='https://github.com/yueiuieui/metal_sc_new',   # 这个是连接，一般写github就可以了，会从pypi跳转到这里去
    install_requires=[              # 这里是依赖列表，表示运行这个包的运行某些功能还需要你安装其他的包
        'easygui',
        'turtle',
        'os',
        'time'
    ]
)
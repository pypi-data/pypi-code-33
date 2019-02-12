
from setuptools import setup
from os import path as os_path


this_directory = os_path.abspath(os_path.dirname(__file__))


def read_file(filename):
    # 读取文件内容
    with open(os_path.join(this_directory, filename), encoding='utf-8') as f:
        long_description = f.read()
    return long_description


def read_requirements(filename):
    # 获取依赖
    return [line.strip() for line in read_file(filename).splitlines()
            if not line.startswith('#')]


long_description = read_file('README.md')
long_description_content_type = "text/markdown",  # 指定包文档格式为markdown


setup(
    name='py_smtp',  # 包名
    python_requires='>=3.4.0',  # python环境
    version='1.0.8',  # 包的版本
    description="send email use smtp",  # 包简介，显示在PyPI上
    long_description=long_description,  # 读取的Readme文档内容
    long_description_content_type=long_description_content_type,  # 指定包文档格式为markdown
    author="HaiFeng",  # 作者相关信息
    author_email='haifengat@vip.qq.com',
    url='https://gitee.com/haifengat',
    # 指定包信息，还可以用find_packages()函数
    # packages=find_packages(),
    packages=['py_smtp'],
    install_requires=read_requirements('requirements.txt'),  # 指定需要安装的依赖
    include_package_data=True,
    license="MIT License",
    platforms="any",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

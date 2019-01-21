from setuptools import setup, find_packages
setup(
    name="Codemao",
    version="0.0.6",
    packages=find_packages(),
    install_requires=[
        'easygui',
        'opencv-python',
        'matplotlib',
        'keras',
        'dlib',
        'tensorflow',
        'pillow',
    ],
    exclude_package_data = {
       'codemao': ['data/*.hdf5',],
    },
    description="Codemao是由深圳点猫科技有限公司创建的一个面向Python初学者的、帮助初学者学习Python的库。 欢迎大家提出各种建议意见，共同讨论学习！",
    author="haiguibainjiqi",
    author_email="wood@codemao.cn",
    url="https://python.codemao.cn/"
)

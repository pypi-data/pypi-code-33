from distutils.core import setup

setup(
    name='ybc_todo',
    version='1.0.14',
    description='Open URL by speech recognition',
    long_description='Open the specified URL by inputting voice',
    author='mengxf',
    author_email='mengxf01@fenbi.com',
    keywords=['pip3', 'todo', 'browser', 'speech recognition', 'url', 'python3', 'python'],
    url='http://pip.zhenguanyu.com/',
    packages=['ybc_todo'],
    package_data={'ybc_todo': ['*.py']},
    license='MIT',
    install_requires=[
        'ybc_speech',
        'ybc_browser',
        'ybc_exception',
        'ybc_tuya',
        'pypinyin'
    ],
)

from setuptools import setup, find_packages

setup(
    name="aihub-things",
    packages=find_packages(),
    version='0.5.0',
    description="aihub things sdk",
    author="zouqqz",
    author_email='zouqqz@gmail.com',
    keywords=['sdk', 'aihub'],
    url='http://github.com',
    install_requires=['paho-mqtt', 'requests', 'CoAPthon'],
)

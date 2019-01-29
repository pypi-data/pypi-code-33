import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='enos-mqtt-sdk-python',
    version='0.0.3',
    author='lihu.yang',
    author_email='lihu.yang@envision-digital.com',
    description='EnOS MQTT SDK for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/EnvisionIot/enos-mqtt-sdk-python.git',
    packages=setuptools.find_packages(),
    install_requires=[
        'atomic >= 0.7.3',
        'futures >= 3.2.0',
        'paho-mqtt >= 1.4.0'
    ],
    classifiers=[
        'Programming Language :: Python :: 2.7'
    ]
)

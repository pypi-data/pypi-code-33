import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='dhtsensor',
    version='0.2.0',
    author='Kent Kawashima',
    author_email='kentkawashima@gmail.com',
    description='Simplifies reading temperature and humidity data from a DHT11/22 sensor using pigpio',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/kentwait/dhtsensor',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    keywords = ['pigpio', 'ir', 'raspberry', 'pi', 'dht11', 'dht22'],
    install_requires=[
        'pigpio',
    ],
)
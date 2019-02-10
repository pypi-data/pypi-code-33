from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='geoClassy',
    version='0.0.7',
    description='a classificator of GPS point over geoJson areas',
    license='MIT',
    packages=['geoClassy'],
    author='Nicola Simboli',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='support@simboli.eu',
    keywords=['geoJson','Open Street Map','gps', 'shapely'],
    url='https://www.simboli.eu/'
)

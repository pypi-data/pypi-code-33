import setuptools

with open("README.md", 'r') as fd:
    longdesc = fd.read()

setuptools.setup(
    name = 'nester-onbon',
    version = '1.0.2',
    py_modules = ['nester'],
    author = 'onbon',
    author_email = 'wangyq@onbonbx.com',
    url = 'http://www.onbonbx.com',
    description = 'This is a simple demo',
    long_description = longdesc,
    long_description_content_type="text/markdown"
)
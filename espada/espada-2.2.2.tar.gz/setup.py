from setuptools import setup

setup(
    name="espada",
    version='2.2.2',
    description='C++ Project and Class Generator',
    url='https://bitbucket.org/cajun_code/espada.py',
    author='Allan Davis',
    author_email='cajun.code@gmail.com',
    license='MIT',
    python_requires='<3.0',
    include_package_data=True,
    packages=['espada'],
    install_requires=[
        'Click',
        'Jinja2',
        'inflection',
    ],
    entry_points='''
        [console_scripts]
        espada=espada:cli
    ''',
    zip_safe=False
)

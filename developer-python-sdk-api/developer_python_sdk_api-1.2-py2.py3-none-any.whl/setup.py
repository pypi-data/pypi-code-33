from setuptools import setup,find_packages
setup(
    name='developer-python-sdk-api',
    version=1.0,
    description=(
        '为开发者的sdk'
    ),
    long_description=open('README.rst').read(),
    author='jiltfly',
    author_email='it.shuaifei@gmail.com',
    maintainer='jiltfly',
    maintainer_email='t-jishuaifei@irootech.com',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'requests>=2.20.1',
    ]
)
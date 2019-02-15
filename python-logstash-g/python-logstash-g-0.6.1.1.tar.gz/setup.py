import setuptools

setuptools.setup(
    name='python-logstash-g',
    packages=['logstash'],
    version='0.6.1.1',
    description='Python logging handler for Logstash.',
    long_description=open('README.rst').read(),
    license='MIT',
    author='Volodymyr Klochan',
    author_email='vklochan@gmail.com',
    url='https://github.com/vklochan/python-logstash',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Logging',
    ]
)

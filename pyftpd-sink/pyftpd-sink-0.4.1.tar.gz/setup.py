from setuptools import setup, find_packages

setup(
    name='pyftpd-sink',
    use_scm_version=True,
    description='write-only ftp server',
    author='Fabian Peter Hammerle',
    author_email='fabian@hammerle.me',
    url='https://git.hammerle.me/fphammerle/pyftpd-sink',
    license='MIT',
    keywords=[
        'ftp',
        'server',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Internet :: File Transfer Protocol (FTP)',
        'Programming Language :: Python',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'pyftpd-sink = pyftpd_sink:main',
        ],
    },
    install_requires=[
        'pyftpdlib>=1.5.4',
    ],
    setup_requires=[
        'setuptools_scm',
    ],
    tests_require=[
        'pytest',
    ],
)

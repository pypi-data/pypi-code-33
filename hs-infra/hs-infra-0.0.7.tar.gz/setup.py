import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='hs-infra',
    version='0.0.7',
    author='Ehsan Sadeghi Neshat',
    author_email='ehsun.zz@gmail.com',
    description='utility and common files in hacker-space projects',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/highborn/hackerspace-software-core-infrastructure.git',
    packages=setuptools.find_packages(),
    install_requires=[
    ],
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)

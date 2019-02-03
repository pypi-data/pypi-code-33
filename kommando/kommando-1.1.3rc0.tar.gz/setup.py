import re
import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()
   
with open('kommando/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

setuptools.setup(
    name='kommando',
    version=version,
    author='Andre Augusto',
    description='A very extensible command parser for discord.py [rewrite]',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Naranbataar/Kommando.py',
    packages=['kommando', 'kommando.defaults'],
    include_package_data=True,
    python_requires='>=3.6.0',
    install_requires=['discord.py>=1.0.0a'],
    classifiers=[
        'Framework :: AsyncIO',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
    ],
)

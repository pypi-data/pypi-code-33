import setuptools

with open("README.md") as fd:
    readme = fd.read()

setuptools.setup(
    name='atbot',
    version='1.0.0',
    author='Naim A.',
    author_email='naim@abda.nl',
    description='Asynchronous Telegram Bot API',
    license='MIT',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/naim94a/atbot',
    packages=setuptools.find_packages(),
    classifiers=(
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
    ),
    project_urls={
        'Issues': 'https://github.com/naim94a/atbot/issues',
        'Pull Requests': 'https://github.com/naim94a/atbot/pulls',
    },
    install_requires=(
        'aiohttp',
    ),
    python_requires='>=3.5.3',
)

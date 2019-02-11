from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='easybot',
    version='0.0.5',
    download_url='https://github.com/BlizardWizard/easybot/archive/0.0.5.tar.gz',
    install_requires=[
        'discord'
    ],
    description='Easy Discord bot library with Python',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/BlizardWizard/Easybot',
    author='Blizard_Wizard',
    author_email='email@robloxcom.me',
    license='MIT',
    packages=['easybot'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
    ],
    keywords=[
        'Discord', 'Python', 'bot', 'easybot', 'easy'
    ],
    zip_safe=False
)

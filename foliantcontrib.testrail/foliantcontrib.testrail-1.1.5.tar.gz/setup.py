from setuptools import setup


SHORT_DESCRIPTION = 'Downloader of test cases from TestRail projects.'

try:
    with open('README.md', encoding='utf8') as readme:
        LONG_DESCRIPTION = readme.read()

except FileNotFoundError:
    LONG_DESCRIPTION = SHORT_DESCRIPTION


setup(
    name='foliantcontrib.testrail',
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    version='1.1.5',
    author='Anton Bukhtiyarov',
    author_email='apkraft@gmail.com',
    url='https://github.com/foliant-docs/foliantcontrib.testrail',
    packages=['foliant.preprocessors.testrail', 'foliant.preprocessors.testrail.testrailapi'],
    package_data={'foliant.preprocessors.testrail': ['case_templates/*.j2']},
    license='MIT',
    platforms='any',
    install_requires=[
        'foliant>=1.0.8',
        'Jinja2'
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Documentation",
        "Topic :: Utilities",
    ]
)

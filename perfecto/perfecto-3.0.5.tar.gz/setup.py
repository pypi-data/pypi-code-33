from distutils.core import setup
release_version = '3.0.5'

setup(
    name='perfecto',
    packages=['perfecto','perfecto/client', 'perfecto/Exceptions', 'perfecto/model', 'perfecto/test'],  # this must be the same as the name above
    version=release_version,
    description='Perfecto Reporting SDK for Python\nPerfecto Reporting is a multiple execution digital report, that enables quick navigation within your latest build execution. Get visibility of your test execution status and quickly identify potential problems with an aggregated report. Hone-in and quickly explore your test results all within customized views, that include logical steps and synced artifacts. Distinguish between test methods within a long execution. Add personalized logical steps and tags according to your team and organization.\n For release notes see: https://github.com/PerfectoCode/Samples/blob/master/Reporting/README.md',
    author='Perfecto',
    author_email='perfecto@perfectomobile.com',
    url='https://github.com/PerfectoCode',  # use the URL to the GitHub repo
    download_url='https://github.com/PerfectoCode',
    keywords=['Perfecto', 'PerfectoMobile', 'Reporting', 'Selenium', 'Appium', 'Automation testing'],
    classifiers=[]
)

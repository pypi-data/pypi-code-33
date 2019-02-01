from setuptools import setup
from setuptools.command.install import install

class PostInstallCommand(install):
    def run(self):
        from pyppeteer.command import install as install_chromium
        install_chromium()
        install.run(self)


setup(
    name='pyppeteer-autoinstall',
    version='0.0.1',
    packages=[],
    install_requires=['pyppeteer'],
    cmdclass={
        'install': PostInstallCommand,
    },
)

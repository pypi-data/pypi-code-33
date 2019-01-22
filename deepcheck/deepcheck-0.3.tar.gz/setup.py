from setuptools import setup, find_packages

setup(
    name='deepcheck',
    packages=find_packages(),
    description='Build and release task for determining neural network susceptibility to adversarial machine learning',
    long_description=open('README.md').read().strip(),
    version='0.3',
    url='',
    license='GPL',
    author='TeamDeepCheck',
    install_requires=['numpy', 'scipy', 'six', 'scikit-learn', 'tensorflow', 'adversarial-robustness-toolbox', 'keras'],
    author_email='',
    keywords=['pip','adversarial machine learning','deep learning']
    )
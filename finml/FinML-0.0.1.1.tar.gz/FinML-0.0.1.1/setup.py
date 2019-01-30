import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='FinML',
    version='v0.0.1.1',
    author='Frank Milthaler',
    author_email='f.milthaler@gmail.com',
    description='A program stock predictions using machine learning methods',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/fmilthaler/FinML',
    license='MIT',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Education',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'],
    keywords=[
        'finance', 'prediction', 'investment',
        'numerical', 'machine learning', 'ML', 'data science',
        'deep learning', 'neural network', 'quantitative', 'quant'],
    python_requires='>=3.5',
    install_requires=['numpy', 'pandas', 'matplotlib'],
    project_urls={'Documentation': 'https://finml.readthedocs.io'}
)

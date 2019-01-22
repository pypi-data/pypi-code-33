from setuptools import setup

setup(
    name='schubert_serpro',
    version='0.0.1',
    description='Consulta rapida de CPF, CNPJ nas bases federais da SERPRO',
    url='https://schubert.gitbook.io/serpro/',
    author='Raphael Schubert',
    author_email='rfswdp@gmail.com',
    license='MIT',
    packages=['schubert_serpro'],
    keywords=['python serpro', 'python3', 'serpro', 'schubert'],
    install_requires=[
        'requests', 'pycpfcnpj'
    ],
    zip_safe=False
)
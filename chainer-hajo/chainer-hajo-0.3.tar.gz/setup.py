from distutils.core import setup

setup(
    name='chainer-hajo',
    version='0.3',
    packages=['chainerhajo',],
    author='Hajo Nils Krabbenhöft',
    url='http://pypi.python.org/pypi/chainer-hajo/',
    license='MIT',
    description='Shared utility classes for Chainer.',
    long_description=open('README.txt').read(),
    setup_requires = ['numpy'],
    install_requires=[
        'chainer>=4.5',
        'opencv-python>=3.4',
        'Pillow>=5.2',
    ],
)

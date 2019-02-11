from distutils.core import setup

setup(
    name='sdebugger',
    packages=['sdebugger'],
    version='0.3',
    license='MIT',
    description='Simple python debugger to keep track of function and running time',
    author='Anh Van Giang',
    author_email='vangianganh@gmail.com',
    url='https://github.com/AnhVanGiang/Simple-Python-Debugger',
    download_url='https://github.com/AnhVanGiang/Simple-Python-Debugger/archive/v_0.3.tar.gz',
    keywords=['DEBUGGER', 'DECORATOR', 'TYPECHECK'],
    install_requires=[
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)

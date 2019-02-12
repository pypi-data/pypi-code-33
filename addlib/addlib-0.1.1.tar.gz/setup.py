from distutils.core import setup, Extension

addlib = Extension(
    'addlib',
    sources=[],
    extra_objects=['addlib/addlib.so'],
)

setup(
    name='addlib',
    version=__import__('addlib').__version__,
    description="Address Library (CN).",
    author='qx3501332',
    author_email='x.qiu@qq.com',
    license="MIT License",
    packages=['addlib'],
    package_data={'addlib': ['lib.add/*.data', 'addlib.so']},
    include_package_date=True,
    zip_safe=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
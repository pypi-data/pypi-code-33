from setuptools import setup
from setuptools.extension import Extension

try:
    from Cython.Distutils import build_ext
except ImportError:
    use_cython = False
else:
    use_cython = True

package_name = 'csiquant'
def make_sources(*module_names):
    file_type = '.pyx' if use_cython else ".cpp"
    return {
        package_name + '.' + module_name : package_name + "/" + module_name + file_type
        for module_name in module_names
    }

sources = make_sources('dimensions', 'quantities')

extensions = [
    Extension(
        module_name,
        sources=[source],
        language='c++',
        include_dirs=["csiquant/"],
        libraries=[]
    )
    for module_name, source in sources.items()
]


CMDCLASS = {}
if use_cython:
    CMDCLASS.update({'build_ext' : build_ext})

INSTALL_REQUIRES = []

TESTS_LIBS = ["pytest"]
DEV_LIBS = ["cython", "bumpversion", "tox"]
EXTRAS_REQUIRE = {
    "tests" : TESTS_LIBS,
    "dev" : TESTS_LIBS + DEV_LIBS
}

KEYWORDS = ["c-extension", "SI", "units", "quantities", "dimensional analysis"]
CLASSIFIERS = [
    "Programming Language :: Python",
    "License :: OSI Approved :: MIT License",
    "Topic :: Scientific/Engineering",
    "Operating System :: OS Independent",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
]

setup(
    name='csiquant',
    author="Greg Echelberger",
    author_email="gechelberger@gmail.com",
    version="1.0.0a1",
    description="cython dimensional analysis and unit tracking utility",
    packages=["csiquant"],
    cmdclass=CMDCLASS,
    setup_requires=["wheel"],
    extras_require=EXTRAS_REQUIRE,
    ext_modules=extensions,
    package_data={
        'csiquant': ['*.pyx', '*.pxd', '*.cpp']
    },
    keywords=KEYWORDS,
    classifiers=CLASSIFIERS,
    zip_safe=False,
)
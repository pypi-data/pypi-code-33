from Cython.Build import cythonize


modules = ['tid/_gettid.pyx']
extensions = cythonize(modules)


def build(setup_kwargs):
    setup_kwargs.update({
        'ext_modules': extensions,
    })

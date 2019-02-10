import pkgutil
import inspect
import importlib
import os


class PyDoc:
    @classmethod
    def find_packages(cls, *names):
        packages = []

        for name in names:
            module = importlib.import_module(name)
            path = module.__path__
            prefix = '{}.'.format(module.__name__)

            packages.extend(
                [i[1] for i in pkgutil.iter_modules(path=path, prefix=prefix)]
            )

        return packages

    @classmethod
    def dir(cls, import_string):
        module = importlib.import_module(import_string)
        members = []

        for attr_name in dir(module):
            if attr_name.startswith('__'):
                continue

            members.append(
                (attr_name, getattr(module, attr_name), )
            )

        return members

    @classmethod
    def get_signature(cls, function):
        pass

    # hooks
    def parser_setup(self, context):
        PYDOC_PACKAGES = getattr(context, 'PYDOC_PACKAGES', [])

        if not PYDOC_PACKAGES:
            return

        packages = self.find_packages(*PYDOC_PACKAGES)

        for package in packages:
            pass

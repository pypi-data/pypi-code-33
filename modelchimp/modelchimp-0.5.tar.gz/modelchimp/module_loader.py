import sys
from importlib.machinery import PathFinder, ModuleSpec, SourceFileLoader


class Finder(PathFinder):
    def __init__(self, module_name, patcher, patchee):
        self.module_name = module_name
        self.patcher = patcher
        self.patchee = patchee

    def find_spec(self, fullname, path=None, target=None):
        if fullname == self.module_name:
            spec = super().find_spec(fullname, path, target)
            loader = CustomLoader(fullname, spec.origin, spec.loader, self.patcher, self.patchee)
            return ModuleSpec(fullname , loader)


class CustomLoader(SourceFileLoader):
    def __init__(self, fullname, path, loader, patcher, patchee_list):
        super().__init__(fullname, path)
        self.patcher = patcher
        self.patchee_list = patchee_list
        self.loader = loader

    def exec_module(self, module):
        #super().exec_module(module)
        self.loader.exec_module(module)

        for patchee in self.patchee_list:
            self._patch_object(patchee, module)

        return module

    def _patch_object(self, patchee, module):
        try:
            patchee_path = patchee.split('.')
            patchee_child = module

            # Access the parent and child objects
            for obj in patchee_path:
                patchee_parent = patchee_child
                patchee_child = getattr(patchee_child, obj)

            # Path the function
            patchee_child = self.patcher(patchee_child)
            setattr(patchee_parent, patchee_path[-1], patchee_child)
        except Exception as e:
            print(e)

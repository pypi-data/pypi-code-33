import sys
import os

# Add autocython dir to the path if we're in the repo. This bit can be left out of
# your own packages, it's just so that the example works without installing
# autocython:
this_folder = os.path.dirname(os.path.abspath(__file__))
grandparent_folder = os.path.abspath(os.path.join(this_folder, '..', '..'))
if os.path.exists(os.path.join(grandparent_folder, 'autocython')):
    sys.path.insert(0, grandparent_folder)


from autocython import ensure_extensions_compiled, import_extension

this_folder = os.path.dirname(os.path.abspath(__file__))

ensure_extensions_compiled(this_folder)
hello_module = import_extension('hello_package.hello_module')
hello = hello_module.hello
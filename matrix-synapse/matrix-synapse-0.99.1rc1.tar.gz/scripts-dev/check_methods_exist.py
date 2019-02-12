
import ast
import importlib
import inspect
import sys


class SelfVisitor(ast.NodeVisitor):
    """Pulls out all attribute access on "self" variables

    Attributes:
        self_attributes(set[str]): Set of names of attributes accessed
            on self. Available after `visit` is called.
    """
    def __init__(self):
        self.self_attributes = set()

    def visit_Attribute(self, node):
        if not isinstance(node.value, ast.Name):
            self.generic_visit(node)
            return

        if node.value.id != "self":
            self.generic_visit(node)
            return

        self.self_attributes.add(node.attr)
        self.generic_visit(node)



def ast_from_class(cls):
    """Given a class object get its ast. Exits if the class
    could not be found.
    """
    class_name = cls.__name__
    tree = ast.parse(inspect.getsource(cls))

    class_node = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        if node.name == class_name:
            class_node = node
            break

    if not class_node:
        print "Failed to find", class_name
        sys.exit(1)

    return class_node


def check_self_access(cls):
    """Prints list of attributes on self that couldn't be found.

    Searches for attributes set by looking at the class's method names,
    attributes set in __init__, and the same for all base classes.
    """

    # Gets a list of classes and base classes
    classes = inspect.getmro(cls)

    # Lets compile lists of known attributes from the class and its parents

    functions = set()  # Found methods
    class_attributes = set()  # Found attributes

    for c in classes:
        if c.__name__ == "object":
            continue

        cnode = ast_from_class(c)

        for node in ast.iter_child_nodes(cnode):
            if not isinstance(node, ast.FunctionDef):
                continue

            if node.name == "__init__":
                # Lets look for attributes assigned to self in __init__
                for child_node in ast.walk(node):
                    if not isinstance(child_node, ast.Attribute):
                        continue

                    if not isinstance(child_node.value, ast.Name):
                        continue

                    if child_node.value.id != "self":
                        continue

                    if isinstance(child_node.ctx, ast.Store):
                        class_attributes.add(child_node.attr)
                continue

            functions.add(node.name)

    # Now lets walk the class to try and find all attribute access on
    # variables named "self"

    for f in functions:
        print f

    print

    class_node = ast_from_class(cls)
    visitor = SelfVisitor()
    visitor.visit(class_node)

    # Print all attributes we didn't know about
    for attr in visitor.self_attributes:
        if attr in functions:
           continue
        if attr in class_attributes:
            continue

        print attr


if __name__ == "__main__":
    # First argument should be a dotted class, e.g.
    # synapse.storage.receipts.ReceiptsStore
    module, clz_name = sys.argv[1].rsplit(".", 1)
    module = importlib.import_module(module)
    clz = getattr(module, clz_name)

    check_self_access(clz)

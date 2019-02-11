import contextlib
import pkg_resources

import six


def enclose_package_path_exists(package_name):
    """
    Returns a `path_exists` method that searches within the specified package
    """
    # NOTE: I don't really like the `enclose_...` name, if anyone wants to
    #       refactor this name, please feel free
    provider = pkg_resources.get_provider(package_name)
    return provider.has_resource


@contextlib.contextmanager
def package_open(package_name, filename):
    """
    Provides a context manager for opening a file within a package.
    If successful, the file will be opened in binary reading mode.

    Example:
        with package_open('some_package', 'path/to/file') as f:
            data = f.read()
    """
    provider = pkg_resources.get_provider(package_name)
    if not provider.has_resource(filename):
        raise IOError('No such file or directory [{}]: {}'.format(package_name, filename))

    manager = pkg_resources.ResourceManager()

    with contextlib.closing(six.BytesIO(provider.get_resource_string(manager, filename))) as f:
        yield f

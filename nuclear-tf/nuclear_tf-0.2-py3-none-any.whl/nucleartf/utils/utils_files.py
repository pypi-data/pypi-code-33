import os


def sub_files(path, endswith=None):
    for root, dirs, files in os.walk(path):
        for file in files:
            if endswith is None or file.endswith(endswith):
                yield os.path.join(root, file)


def path_listdir(dirname, prefix=None, only_files=False):
    result = [os.path.join(dirname, basename)
              for basename in os.listdir(dirname)
              if not prefix or basename.startswith(prefix)]
    if only_files:
        result = list(map(os.path.isfile, result))
    result.sort()
    return result


def home_path():
    return os.path.expanduser('~')

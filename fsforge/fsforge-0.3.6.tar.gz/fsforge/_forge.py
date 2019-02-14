import os
import sys


if sys.version_info[0] == 3:
    str_types = str
else:
    str_types = (str, unicode)  # noqa: F821 undefined name (in python3)


def nicer_fs_repr(fs_tree):
    """
        Return a string with "nicer" layout of a fs_tree (newlines, indents, sorted keys).
    """
    assert isinstance(fs_tree, dict), "Expected fs_tree to be a dictionary, got {}".format(type(fs_tree).__name__)

    def elements(tree, indent_level):
        directories, files = _split_by_type(tree)
        indent = "    " * indent_level
        for dir_name, sub_tree in sorted(directories.items()):
            sub_repr = ",".join(elements(sub_tree, indent_level + 1))
            yield "\n{ind}{name!r}: {{{sub}\n{ind}}}".format(name=dir_name, sub=sub_repr, ind=indent)

        for file_name, contents in sorted(files.items()):
            yield "\n{ind}{name!r}: {value!r}".format(name=file_name, value=contents, ind=indent)

    return "{{{}\n}}\n".format(",".join(elements(fs_tree, 1)))


def is_directory(tree_item):
    return isinstance(tree_item[1], dict)


def _split_by_type(fs_tree):
    directories = []
    files = []

    for tree_item in fs_tree.items():
        if is_directory(tree_item):
            directories.append(tree_item)
        else:
            files.append(tree_item)

    return dict(directories), dict(files)


def _walk_equivalent(dir_path, dir_tree, joiner=os.path.join):
    def _prepend_path(root, *trees):
        return tuple({joiner(root, k): v for k, v in tree.items()} for tree in trees)

    directories, files = _prepend_path(dir_path, *_split_by_type(dir_tree))

    yield directories, files
    for sub_dir_path, sub_dir_tree in directories.items():
        for result in _walk_equivalent(sub_dir_path, sub_dir_tree, joiner):
            yield result


def pyfakefs_args_translator(file_parameter, _):
    """ a hook that will prepare arguments to call pyfakefs.create_file() or your custom fs_creator

        For fs_creator being pyfakefs.FakeFilesystem it can produce the following args:
        file_path           - The path to the file to create.
        st_mode             - The stat constant representing the file type.
        contents            - The contents of the file.
        st_size             - The file size; only valid if contents not given.
        create_missing_dirs - If True, auto create missing directories.
        apply_umask         - True if the current umask must be applied on st_mode.
        encoding            - If contents is a unicode string, the encoding used for serialization.
        errors              - The error mode used for encoding/decoding errors.

        The resulting dictionary will be bassed to each call of fs_creator.create_file()
    """
    if isinstance(file_parameter, str_types):
        " Treat the argument as being 1:1 content of the file. "
        args = dict(contents=file_parameter)

    elif isinstance(file_parameter, int):
        " For creating dummy files - just acting by existence and artificial file size. "
        args = dict(st_size=file_parameter)

    else:
        " 'touch' case, creates empty file with zero size."
        args = dict()

    return args


def create_fs(fs_creator, fs_tree_dict, root_mount_point, args_translator=pyfakefs_args_translator):
    """
        Helper for pyfakefs to create artificial filesystem structure and its contents with
        nice and syntactically clear python's dict literals.

        It's opposite to: take_fs_snapshot(root_mount_point)

        fs_creator is pyfakefs.FakeFilesystem instance, but can be any object exposing
        create_dir and create_file interface that reaches your goal. Providing a custom fs_creator you
        will probably need to change also args_translator.
    """

    assert hasattr(fs_creator, "create_dir"), "Fs creator has to implmement 'create_dir' method"
    assert hasattr(fs_creator, "create_file"), "Fs creator has to implmement 'create_file' method"

    assert isinstance(fs_tree_dict, dict), 'Expecting a dictionary as an argument.'
    assert isinstance(root_mount_point, str_types), 'Expecting root_mount_point to be a string.'

    if not os.path.exists(root_mount_point):
        fs_creator.create_dir(root_mount_point)

    for directories, files in _walk_equivalent(root_mount_point, fs_tree_dict):
        for directory_path in directories:
            fs_creator.create_dir(directory_path)

        for file_path, file_content in files.items():
            args = args_translator(file_content, file_path)
            fs_creator.create_file(file_path, **args)

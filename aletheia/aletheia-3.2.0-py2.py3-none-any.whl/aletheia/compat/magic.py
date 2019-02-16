import magic


def get_mimetype(path):
    """
    Handle the case where we've got multiple incarnations of the magic module
    installed.  If we're dealing with the python-magic module (on Alpine
    systems), then we use ``.from_file()``, otherwise we use the file-magic
    module's ``detect_from_filename()``.
    """
    if hasattr(magic, "from_file"):  # python-magic
        return magic.from_file(path, mime=True)
    return magic.detect_from_filename(path).mime_type

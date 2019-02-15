import uuid

from django.conf import settings


def upload(file):
    # TODO: add slashes, create directory to bypass files count limitation.
    suffix = str(uuid.uuid4())

    parts = file.name.split(".")
    if len(parts) >= 2:
        extension = '.{}'.format(parts[-1])
    else:
        extension = ''

    path = "{}/{}{}".format(
        settings.DSL_UPLOAD_DIRECTORY,
        suffix,
        extension
    )

    with open(path, "wb") as handle:
        handle.write(
            b"".join([chunk for chunk in file.chunks()])
        )

    return "{}{}".format(suffix, extension)

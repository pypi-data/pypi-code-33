import os

import magic
from django.forms import ValidationError
from django.template.defaultfilters import filesizeformat


class FileContentValidator:
    def __init__(self, min_size=None, max_size=None, content_restrictions=[]):
        self.min_size = min_size
        self.max_size = max_size
        self.content_restrictions = content_restrictions

    def __call__(self, value):
        if self.min_size and value.size < self.min_size:
            raise ValidationError(
                "Размер файла должен быть больше {}. Текущий размер {}.".format(
                    filesizeformat(self.min_size),
                    filesizeformat(value.size)
                )
            )

        if self.max_size and value.size > self.max_size:
            raise ValidationError(
                "Размер файла должен быть меньше {}. Текущий размер {}.".format(
                    filesizeformat(self.max_size),
                    filesizeformat(value.size)
                )
            )

        if not self.content_restrictions:
            return

        extension = os.path.splitext(value.name)
        if len(extension) != 2:
            raise ValidationError("Файлы данного типа не поддерживаются.")

        extension = extension[1].replace(".", "").lower()
        content_type = magic.from_buffer(value.read(), mime=True)
        success_flag = False

        for content_restrictions in self.content_restrictions:
            if extension not in content_restrictions["extensions"]:
                continue

            if content_type not in content_restrictions["content_types"]:
                continue

            success_flag = True
            break

        if not success_flag:
            raise ValidationError("Файлы данного типа не поддерживаются.")

class TemplateNotDefinedException(Exception):
    message = 'Call to get_absolute_path without template parameter and no template set'


class FileNotLoadedException(Exception):
    message = 'Could not load file'


class IndentationException(Exception):
    message = 'Indentation not a multiple of two'


class VariableNotDefinedException(Exception):
    message = 'Variable not defined'


class TranslationNotDefinedException(Exception):
    message = 'Translation not defined'

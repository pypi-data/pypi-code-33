from flake8.formatting import default
from flake8.style_guide import Violation


ENTRY_POINT_NAME = "rewriter"


class FakeStr(str):
    """
    Class that acts like a string, but .append adds to an inner list.
    This allows this plugin to record changes to options, but "trick" flake8 into 
    using rewrite as the formatter.
    """
    def __new__(cls, value):
        obj = super(FakeStr, cls).__new__(cls, value)
        obj.appended = []
        return obj

    def append(self, str):
        self.appended.append(str)


def force_option_callback(option, opt_str, value, parser, *args, **kwargs):
    if hasattr(parser.values, "format"):
        # Ignore appending existing values of default or rewriter
        if parser.values.format == "default" or parser.values.format == ENTRY_POINT_NAME:
            parser.values.format = FakeStr(ENTRY_POINT_NAME)
        else:
            new_value = FakeStr(ENTRY_POINT_NAME)
            new_value.append(parser.values.format)
            parser.values.format = new_value
    else:
        setattr(parser.values, "format", FakeStr(ENTRY_POINT_NAME))
    
    parser.get_option("--format").action = "append"

def add_options(option_manager):
    option_manager.add_option(
        "--replace",
        action="append",
        dest="replacements",
        help="Given <code1>:<code2>, replaces all instances of <code1> with <code2>.")

    option_manager.add_option(
        "--force-rewriter",
        action="callback",
        callback=force_option_callback,
        help="Force enables rewriter."
    )

def rewrite_violation(violation, new_code):
    return Violation(
        new_code,
        violation.filename,
        violation.line_number,
        violation.column_number,
        violation.text,
        violation.physical_line)


class RewriteFormatter(default.SimpleFormatter):
    error_format = "%(path)s:%(row)d:%(col)d: %(code)s %(text)s"
    add_options = add_options

    def __init__(self, options):
        super().__init__(options)

        self.replacements = dict()
        if hasattr(options, "replacements"):
            for k, v in map(lambda s: s.split(":", 1), options.replacements):
                self.replacements[k] = v
    
    def after_init(self):
        """Checks the FakeStr for any custom formats that may have been applied"""
        if self.options.format.appended:
            self.error_format = self.options.format.appended[0]

    def format(self, error):
        if error.code in self.replacements:
            error = rewrite_violation(error, self.replacements[error.code])

        return super().format(error)
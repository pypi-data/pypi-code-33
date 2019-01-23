import sys
from PyInquirer import prompt


def ask_continue_on_invalid(name):
    message = (
        "Could not validate `{0}` data, (errors are shown above). "
        "Continue without `{0}` data?".format(name)
    )
    q = [{"type": "confirm", "name": "continue", "default": True, "message": message}]
    if not prompt(q)["continue"]:
        sys.exit(1)

# ------- #
# Imports #
# ------- #

from ..fns import isEmpty, isSomething, raise_
from os import path


# ---- #
# Main #
# ---- #


def validateRunParams(projectDir, reporter, silent):
    if isSomething(projectDir):
        if not isinstance(projectDir, str):
            raise_(
                TypeError,
                f"""\
                'projectDir' must be an instance of str
                type: {type(silent).__name__}
                """,
            )

        if isEmpty(projectDir):
            raise ValueError("'projectDir' cannot be an empty string")

        if not path.isabs(projectDir):
            raise_(
                ValueError,
                f"""
                'projectDir' must pass 'os.path.isabs'
                projectDir: {projectDir}
                """,
            )

        if not path.isdir(projectDir):
            raise_(
                ValueError,
                f"""
                'projectDir' must pass 'os.path.isdir'
                projectDir: {projectDir}
                """,
            )

    if isSomething(reporter):
        if not isinstance(reporter, str):
            raise_(
                TypeError,
                f"""
                'reporter' must be an instance of str
                type: {type(reporter).__name__}
                """,
            )

        if isEmpty(reporter):
            raise ValueError("'reporter' cannot be an empty string")

        if reporter.startswith("."):
            raise_(
                ValueError,
                f"""
                relative reporter modules are not yet supported
                reporter: {reporter}
                """,
            )

    if isSomething(silent) and not isinstance(silent, bool):
        raise_(
            TypeError,
            f"""\
            'silent' must be an instance of bool
            type: {type(silent).__name__}
            """,
        )

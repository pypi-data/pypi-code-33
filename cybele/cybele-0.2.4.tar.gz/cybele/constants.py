import os


USER_NAME = os.getlogin()
USER_HOME = os.path.expanduser("~")
CYBELE_DIRNAME = ".cybele"
DEFAULT_DB_PATH = os.path.join(USER_HOME, CYBELE_DIRNAME, f"{USER_NAME}.cybeledb")

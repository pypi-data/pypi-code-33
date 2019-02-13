from horetu import cli, Program
from . import send_files

cli(Program(
    send_files,
    name='send-files',
))


import sys

from kabaret.app.ui import cli


class MyStudioCLISession(cli.KabaretCLISession):

    pass


if __name__ == '__main__':
    argv = sys.argv[1:]  # get ride of first args wich is script filename
    host, port, cluster_name, session_name = MyStudioCLISession.parse_command_line_args(
        argv
    )
    session = MyStudioCLISession(session_name=session_name)
    session.cmds.Cluster.connect(host, port, cluster_name)
    session.start()
    session.close()

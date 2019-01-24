# -*- coding: utf-8 -*-
import sys

from docopt import docopt
from rockset import version
from rockset.credentials import Credentials
from rockset.exception import AuthError

def main(args=None):
    # init args from sys
    if args is None:
        args = sys.argv[1:]

    usage = """usage: rock [--version] [--help]
       rock [-v | -vv | -vvv] [options] <command> [<args> ...]
       rock help <command>

Command line interface to Rockset

Options:
  --version                  display rockset version and exit

  -h, --help                 print help message and exit
  -o, --format=FORMAT        select output format; one of {json,text,yaml}
                             [default: text]
  -p, --profile=PROFILE      select name of the credentials profile to use
  -v, --verbose              increase output verbosity

Commands:

  Setup Credentials:
       configure             setup auth credentials via API keys

  Data Definition:
       create                create a new collection or integration
       describe              get detailed stats about a collection or integration
       drop                  drop an existing collection or integration
       ls                    list all collections or integrations

  Data Management:
       get                   retrieve documents from a collection
       rm                    remove a document from a collection
       sql                   run a SQL query from command-line or
                             enter SQL REPL when run without any args
       upload                upload local files to a collection

  Other Commands:
       help                  more information on a specific command
       play                  play a game of {rock,paper,scissors}


Use 'rock help <command>' for more information on a specific command.
"""
    parsed_args = docopt(usage, argv=args, help=False, version=version(),
        options_first=True)

    # setup command and args
    command = parsed_args['<command>']
    argv = [command] + parsed_args['<args>']

    # setup credentials
    Credentials().setup()

    # process the command - delayed imports save load time for every run
    if command == 'configure':
        from rockset.rock.commands.configure import Configure
        command_cls = Configure
    elif command == 'create':
        from rockset.rock.commands.create import Create
        command_cls = Create
    elif command == 'describe':
        from rockset.rock.commands.describe import Describe
        command_cls = Describe
    elif command == 'drop':
        from rockset.rock.commands.drop import Drop
        command_cls = Drop
    elif command == 'ls':
        from rockset.rock.commands.list import List
        command_cls = List
    elif command == 'upload':
        from rockset.rock.commands.upload import Upload
        command_cls = Upload
    elif command == 'get':
        from rockset.rock.commands.get import Get
        command_cls = Get
    elif command == 'rm':
        from rockset.rock.commands.remove import Remove
        command_cls = Remove
    elif command == 'sql':
        from rockset.rock.commands.sqlquery import SQLQuery
        command_cls = SQLQuery
    elif command == 'play':
        from rockset.rock.commands.play import Play
        command_cls = Play
    elif command == 'help':
        argv = parsed_args['<args>'] + ['--help']
        main(args=argv)
        return 0
    else:
        print(usage)
        return 0

    # catch exceptions in constructor
    try:
        c = command_cls(**parsed_args)
    except AuthError as e:
        print('Error: {}'.format(str(e)), file=sys.stderr)
        print('Hint: Use "rock configure" to update your credentials.',
            file=sys.stderr)
        return 1
    except Exception as e:
        print('Error: {} {}'.format(type(e).__name__, str(e)), file=sys.stderr)
        return 1

    # let Command.main_go() deal with all exceptions here
    return c.main(argv)


if __name__ == '__main__':
    main()

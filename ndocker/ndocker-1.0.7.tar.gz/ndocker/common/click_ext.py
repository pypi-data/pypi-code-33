from click import Command
from click import Group
from click.decorators import command

class MyCommand(Command):
    def __init__(self, name, section='Commands', **attrs):
        Command.__init__(self, name, **attrs) 
        self.section = section

class MyGroup(Group):
    def __init__(self, section='Commands', **attrs):
        super(MyGroup, self).__init__(**attrs)
        self.section = section
    
    def format_commands(self, ctx, formatter):
        """Extra format methods for multi methods that adds all the commands
        after the options.
        """
        d = dict()
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command.  Ignore it
            if cmd is None:
                continue

            help = cmd.short_help or ''

            section = 'Commands'
            if isinstance(cmd, MyGroup):
                section = getattr(cmd, 'section')

            rows = d.get(section, list())
            rows.append((subcommand, help))
            d[section] = rows
        
        for key, value in d.items():
            if len(value)>0:
                with formatter.section(key):
                    formatter.write_dl(value)

def group(name=None, **attrs):
    """Creates a new :class:`Group` with a function as callback.  This
    works otherwise the same as :func:`command` just that the `cls`
    parameter is set to :class:`Group`.
    """
    attrs.setdefault('cls', MyGroup)
    return command(name, **attrs)

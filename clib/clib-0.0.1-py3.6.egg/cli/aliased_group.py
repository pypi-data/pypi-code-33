import click


class AliasedGroup(click.Group):
    """
    A simple click.Group subclass that allows running commands using
    a shortened form (e.g. first or first couple of letters).

    It also allows registering custom alias to command mappings.

    Taken from:
    http://click.pocoo.org/5/advanced/#command-aliases
    """

    def register_alias(self, alias_name=None, command_name=None):
        """ Register an alias_name -> command_name mapping.

        Params:
            alias_name: The name of the alias to create
            command_name: The command to map the alias to

        Raises:
            ValueError: raise value error for missing or identical params.
        """

        if alias_name == command_name or None in [alias_name, command_name]:
            raise ValueError(
                "alias_name and command_name must be specified and different"
            )

        if not hasattr(self, "aliases"):
            setattr(self, "aliases", {})

        self.aliases[alias_name] = command_name

    def get_command(self, ctx, cmd_name):
        """ Get a command by alias, short name, or full name.
        """

        command_name = cmd_name
        commands = self.list_commands(ctx)

        if cmd_name in getattr(self, "aliases", {}):
            command_name = self.aliases.get(cmd_name)

        if command_name not in commands:
            matches = list(
              filter(
                lambda x: x.startswith(cmd_name),
                commands + getattr(self, "aliases", {}).keys()
              )
            )

            if len(matches) > 1:
                return ctx.fail(
                    'Too many matches: {}'.format(', '.join(sorted(matches)))
                )

            if len(matches) < 1:
                return ctx.fail('No matching command or alias')

            if matches[0] in commands:
                command_name = matches[0]
            else:
                command_name = self.aliases.get(matches[0])

        return click.Group.get_command(self, ctx, command_name)

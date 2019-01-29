from intermake.engine import Visibility


def __is_cli() -> bool:
    from intermake.engine import Controller, EImRunMode
    return EImRunMode.is_console( Controller.ACTIVE.mode )


COMMON = Visibility( name = "common",
                     comment = "Common commands. Visible by default." )

ADVANCED = Visibility( name = "advanced",
                       is_visible = False,
                       comment = "Advanced commands. Hidden by default." )

CLI = Visibility( name = "cli",
                  is_visible = __is_cli,
                  comment = "Commands best suited to the CLI." )

INTERNAL = Visibility( name = "internal",
                       is_useful = False,
                       comment = "Commands for use internally." )

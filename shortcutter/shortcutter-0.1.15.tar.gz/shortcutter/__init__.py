from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

import os
import sys

# operating system specific imports
if os.name == 'nt':
    from .windows import ShortCutterWindows as ShortCutter
elif os.name == 'posix':
    if sys.platform == 'darwin':
        from .macos import ShortCutterMacOS as ShortCutter
    else:
        from .linux import ShortCutterLinux as ShortCutter
else:
    raise Exception("Error: '{}' platform is not supported.".format(sys.platform))


def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Automatic shortcut creator." +
                                        " Shortcuts auto-activate their environments by default.")
    parser.add_argument("target", nargs='?', default=None,
                        help="The target executable to create Desktop and Menu shortcuts.")
    parser.add_argument("-d", "--desktop", action="store_true", help="Only create a desktop shortcut.")
    parser.add_argument("-m", "--menu", action="store_true", help="Only create a menu shortcut.")
    parser.add_argument("-n", "--name", nargs='?', default=None, help="Name of the shortcut without extension (autoname otherwise).")
    parser.add_argument("-s", "--simple", action="store_true", help="Create simple shortcut without activate wrapper.")
    parser.add_argument("-t", "--terminal", action="store_true",
                        help="Create shortcut to environment with shortcutter " +
                             "(plus shortcut to root environment in case of conda).")
    args = parser.parse_args()

    create_desktop = args.desktop
    create_menu = args.menu
    activate = not args.simple
    name = args.name if args.name else None

    if not args.target and not args.terminal:
        print('Shortcutter needs target or --terminal arguments to work.')
        return

    # if desktop or menu hasnt been specified create both (i.e. the default)
    if not create_desktop and not create_menu:
        create_desktop = True
        create_menu = True

    sc = ShortCutter(activate=activate, error_log=sys.stdout)

    target_path = sc.find_target(args.target)
    if target_path or args.terminal:

        desktop_created = False
        if create_desktop:
            if args.terminal:
                desktop_created = sc.create_shortcut_to_env_terminal(name, menu=False)
            else:
                ret = sc.create_desktop_shortcut(target_path, name)
                desktop_created = bool(ret[2])  # shortcut_path = ret[2]
            if not desktop_created:
                print("Failed to create desktop shortcut.")

        menu_created = False
        if create_menu:
            if args.terminal:
                menu_created = sc.create_shortcut_to_env_terminal(name, desktop=False)
            else:
                ret = sc.create_menu_shortcut(target_path, name)
                menu_created = bool(ret[2])  # shortcut_path = ret[2]
            if not menu_created:
                print("Failed to create menu shortcut.")

        msg = "created for '{}'.".format(args.target if not args.terminal else 'terminal at environment')
        if desktop_created and menu_created:
            print('Desktop and menu shortcuts were ' + msg)
        elif desktop_created and not menu_created:
            print('Desktop shortcut was ' + msg)
        elif not desktop_created and menu_created:
            print('Menu shortcut was ' + msg)
    else:
        print("Shortcut creation failed: unable to find '{}'.".format(args.target))

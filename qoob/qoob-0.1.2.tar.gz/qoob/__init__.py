#!/usr/bin/python3
from PyQt5 import QtDBus
import sys


def main():
    bus = QtDBus.QDBusConnection.sessionBus()
    interface = QtDBus.QDBusInterface("org.qoob.session", "/org/qoob/session", "org.qoob.session", bus)
    cmd = "%".join(str(arg) for arg in sys.argv[1:])

    # Pass the arguments to the existing bus
    if interface.isValid():
        interface.call("parse", cmd)
        sys.exit(0)

    # Create a new instance
    elif not cmd.lower().count("--quiet"):
        try:
            import qoob.main as qoob
        except ImportError:
            import main as qoob
        qoob.main(cmd)

if __name__ == '__main__':
    main()

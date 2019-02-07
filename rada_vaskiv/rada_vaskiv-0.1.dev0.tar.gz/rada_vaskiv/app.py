from rada_vaskiv.consoles import UkraineConsole, PolandConsole
from rada_vaskiv.models import *


def main():
    console = PolandConsole(PolandRada, PolandFraction, PolandDeputat)
    console.run()


if __name__ == '__main__':
    main()

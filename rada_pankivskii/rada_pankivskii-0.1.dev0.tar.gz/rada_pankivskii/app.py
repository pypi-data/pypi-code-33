from rada_pankivskii.consoles import UkraineConsole, PolandConsole
from rada_pankivskii.models import *


def main():
    # console = UkraineConsole(UkraineRada, UkraineFraction, UkraineDeputat)
    console = PolandConsole(PolandRada, PolandFraction, PolandDeputat)
    console.run()


if __name__ == '__main__':
    main()

from rada_package_budzsergiy.consoles import UkraineConsole, PolandConsole
from rada_package_budzsergiy.models import *


def main(name):
    # nam
    # if name == "україна":
    #     console = UkraineConsole(UkraineRada, UkraineFraction, UkraineDeputat)
    #     console.run()

    # elif name == 'польща':
        console = PolandConsole(PolandRada, PolandFraction, PolandDeputat)
        console.run()


if __name__ == '__main__':
    # name = input("Яка рада? ")
    main(name)
    main()

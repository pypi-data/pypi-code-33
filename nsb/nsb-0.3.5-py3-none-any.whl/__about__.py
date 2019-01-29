__author__ = "Matthias Buechele"
__author_email__ = "matthias.buechele@fau.de"
__maintainer__ = __author__
__email__ = __author_email__
__copyright__ = "Copyright 2017, Matthias Buechele"
__credits__ = ["Matthias Buechele"]
__license__ = "GNU GPL v3"
__shortname__ = "nsb"
__description__ = 'Draws nightsky allskymaps',
__long_description__ = ("Draws nightsky allskymaps corresponding to KRISCIUNAS Model of the Brightness of Moonlight,\n"
                "together with star data obtained from the GAIA public data release catalog.\n"
                "The result is a 2D Pixel array with physical brightness values for each sky position.\n\n"
                "Or estimate the brightness for a given source over a timespann. The GAIA Data will we automatically downloaded via an query to the corresponding ESA server. The User has just decide how much to get. For calling sources 'by name' and storing their positions, nsb includes a sub packages 'mypycat'. Therefore a catalog is needed, which is not provided. Only a dummy file will be created and the user is free to add any source coordinates to  ~./nsb/mypycat.txt")
__status__ = "Development"  # "Prototype", "Development", or "Production"
__version__ = "0.3.5"

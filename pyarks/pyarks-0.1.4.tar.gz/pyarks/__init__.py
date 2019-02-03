from __future__ import print_function
from .universal.IslandsOfAdventure import IslandsOfAdventure
from .universal.UniversalStudiosFlorida import UniversalStudiosFlorida
from .universal.VolcanoBay import VolcanoBay
from .universal.UniversalStudiosHollywood import UniversalStudiosHollywood

__version__ = "0.1.4"

name = "pyarks"

parks = {
    'islandsOfAdventure': IslandsOfAdventure,
    'universalStudiosFlorida': UniversalStudiosFlorida,
    'volcanoBay': VolcanoBay,
    'universalStudiosHollywood': UniversalStudiosHollywood
}

def getPark(name):
    if name == "USF" or name == "Universal Studios Florida":
        return UniversalStudiosFlorida()
    elif name == "VB" or name == "Volcano Bay":
        return VolcanoBay()
    elif name == "IOA" or name == "Islands of Adventure":
        return IslandsOfAdventure()
    elif name == "USH" or name == "Universal Studios Hollywood":
        return UniversalStudiosHollywood()
    else:
        print("Unsupported park name")
        print("Currently the module supports 'USF', 'USH', 'VB' and 'IOA'")
        print("Returning None")
        return None

"""
allskymaps python package.

Draws Allsky Nightsky Images with stars from the GAIA catalog

    This work has made use of data from the European Space Agency (ESA)
    mission {\\it Gaia} (\\url{https://www.cosmos.esa.int/gaia}), processed by
    the {\\it Gaia} Data Processing and Analysis Consortium (DPAC,
    \\url{https://www.cosmos.esa.int/web/gaia/dpac/consortium}). Funding
    for the DPAC has been provided by national institutions, in particular
    the institutions participating in the {\\it Gaia} Multilateral Agreement.

and draws moonlight corresponding to the Model from Krisciunas et al.

   author = {{Krisciunas}, K. and {Schaefer}, B.~E.},
    title = "{A model of the brightness of moonlight}",
  journal = {\pasp},
     year = 1991,
    month = sep,
   volume = 103,
    pages = {1033-1039},
      doi = {10.1086/132921},
   adsurl = {http://adsabs.harvard.edu/abs/1991PASP..103.1033K},


This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

Created and maintained by Matthias Buechele [FAU].

"""


import numpy as np
import time
import math
import matplotlib.pyplot as plt
import matplotlib.cm as cm


def writeToDataFile(filename, values):
    '''
    Very simple Function to write (append) some values to a file
    '''
    f = open(filename, 'a')
    f.write(values)
    f.close()


def plotMaps(images):
    print('Please close Plot Window to proceed (terminate)...')
    if len(images) == 1:
        vmin, vmax = np.nanmin(images[0].fitsfile.data), np.minimum(2 * np.nanmedian(images[0].fitsfile.data),
                                                                    np.nanmax(images[0].fitsfile.data))
        plt.imshow(images[0].fitsfile.data, cmap=cm.viridis, vmin=vmin, vmax=vmax)
        plt.colorbar()
        plt.gca().get_xaxis().set_visible(False)
        plt.gca().axes.get_yaxis().set_visible(False)
        plt.title('Allskymaps for %s\n(Lon %.4f | Lat %.4f)' % (images[0].site.date, math.degrees(images[0].site.lon), math.degrees(images[0].site.lat)))
        plt.show()
    elif len(images) == 2:
        fig, (sub1, sub2) = plt.subplots(1, 2)
        fig.suptitle('skymaps for %s\n(Lon %.4f | Lat %.4f)' % (
        images[0].site.date, math.degrees(images[0].site.lon), math.degrees(images[0].site.lat)))

        sub1.get_xaxis().set_visible(False)
        sub1.axes.get_yaxis().set_visible(False)
        sub2.get_xaxis().set_visible(False)
        sub2.axes.get_yaxis().set_visible(False)

        sub1.set_title('All-Sky')
        sub2.set_title('FOV %.1f°\nalt %.1f az %.1f' % (images[1].fov,math.degrees(images[1].alt), math.degrees(images[1].az)))

        vmin, vmax = np.nanmin(images[0].fitsfile.data), np.minimum(2 * np.nanmedian(images[0].fitsfile.data),
                                                                    np.nanmax(images[0].fitsfile.data))
        im1 = sub1.imshow(images[0].fitsfile.data, cmap=cm.viridis, vmin=vmin, vmax=vmax)
        vmin, vmax = np.nanmin(images[1].fitsfile.data), np.minimum(2 * np.nanmedian(images[1].fitsfile.data),
                                                                    np.nanmax(images[1].fitsfile.data))
        im2 = sub2.imshow(images[1].fitsfile.data, cmap=cm.viridis, vmin=vmin, vmax=vmax)

        fig.colorbar(im1, ax=sub1, orientation="horizontal")
        fig.colorbar(im2, ax=sub2, orientation="horizontal")

        plt.show()
    else:
        raise NotImplementedError("We did not expect to get more than 2 images for plotting")


def makeDateString(date):

    d = date.tuple()
    date_string = ''
    for x in d:
        if float(x) < 1:
            x = 0
        if len(str(int(x))) > 1:
            date_string += str(int(x))
        elif len(str(int(x))) == 1:
            date_string += '0' + str((x))
    return date_string

def makeDate(datestring, timestring):
    if datestring in ['today', 'heute']:
        year = time.strftime("%Y")
        month = time.strftime("%m")
        day = time.strftime("%d")
    else:
        year = datestring[0:4]
        month = datestring[5:7]
        day = datestring[8:]

    if timestring in ['now', 'jetzt']:
        hour = time.strftime("%H")
        minute = time.strftime("%M")
        second = time.strftime("%S")
    else:
        hour = timestring[0:2]
        minute = timestring[3:5]
        second = timestring[6:]

    return "" + str(year) + "/" + str(month) + "/" + str(day) + " " \
                + str(hour) + ":" + str(minute) + ":" + str(second)


def nLbMag(B):
    '''
    nanoLambert to Magnitude conversion
    '''
    return -2.5 * math.log10(1.0 / np.pi * 0.00001 * B / 108400.0)


def MagnLb(M):
    '''
    Magnitude to nanoLambert conversion
    '''
    return np.pi * 100000 * 108400 * 10**(-0.4 * M)


def greatCircle(Zen, phi, Zen2, phi2):
    '''
    Calculates the great Circle Distance of two pairs of spheric coordinates
    Works for GPS Coordinates as well as for Zen / Az (not ALT !)
    '''
    if Zen == Zen2 and phi == phi2:
        return 0
    else:
        return math.acos(math.sin(np.pi / 2. - Zen) * math.sin(np.pi / 2. - Zen2) +
                         math.cos(np.pi / 2. - Zen) * math.cos(np.pi / 2. - Zen2) * math.cos(phi - phi2))


def X(Z):
    return 0.4 + 0.6 * (1 - 0.96 * (math.sin(Z))**2)**(-0.5)


def f(rho):
    r = math.degrees(rho)
    A = 5.2313
    B = 0.9351
    F = 5.9014
    return 10**A * (B + (math.cos(rho))**2) + 10**(F - r / 40)


def I_moon(moon_alpha):
    a = math.degrees(moon_alpha)
    return 10**(-0.4 * (3.84 + 0.026 * math.fabs(a) + 4 * 10**(-9) * a**4))


def B_sky(Zen, phi, B_zero, k):
    """
    Krisciunas et. al Sky-only-Model
    Brightness of the Sky at certain position without moon
    """
    if Zen < np.pi / 2:
        return B_zero * X(Zen) * 10**(-0.4 * k * (X(Zen) - 1))
    else:
        return 0


def B_moon(Zen, phi, Zen_moon, phi_moon, k, moon_alpha):
    """
    Krisciunas et. al Moon-Model
    only valid for moon above horizon. it gives values for negative moon alt,
    but they have no physical meaning.
    --> so in that case better return 0
    """
    if Zen_moon < np.pi / 2:
        rho = greatCircle(Zen, phi, Zen_moon, phi_moon)
        return f(rho) * I_moon(moon_alpha) * 10**(-0.4 * k * X(Zen_moon)) * (1 - 10**(-0.4 * k * X(Zen)))
    else:
        return 0


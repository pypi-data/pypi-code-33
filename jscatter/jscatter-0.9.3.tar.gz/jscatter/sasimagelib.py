# -*- coding: utf-8 -*-
# written by Ralf Biehl at the Forschungszentrum Jülich ,
# Jülich Center for Neutron Science 1 and Institute of Complex Systems 1
#    Jscatter is a program to read, analyse and plot data
#    Copyright (C) 2015  Ralf Biehl
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Read 2D image files (TIFF) from SAXS cameras and extract the corresponding data.

The sasImage is a 2D array that allows direct subtraction and multiplication (e.g. transmission)
respecting given masks in operations. E.g. ::

 sample=js.sas.sasImage('sample.tiff')
 solvent=js.sas.sasImage('solvent.tiff')
 corrected = sample/sampletransmission - solvent/solventtransmission

Calibration of detector distance, radial average, size reduction and more.
.pickBeamcenter allows sensitive detection of the beamcenter.

An example is shown in :py:class:`~.sasimagelib.sasImage` .


------

"""

import os
import glob
import copy
import time
import numpy as np
import numpy.ma as ma
import scipy
import scipy.linalg as la
from scipy import ndimage
from scipy.interpolate import griddata
import PIL
import PIL.ImageOps
import PIL.ExifTags
import PIL.ImageSequence
from xml.etree import ElementTree
import matplotlib
import matplotlib.cm as cm
from matplotlib import colors
from matplotlib.patches import Circle
from matplotlib import pyplot

from . import formel
from .dataarray import dataArray as dA
from .dataarray import dataList as dL
from . import mpl

try:
    basestring
except NameError:
    basestring = str

# normalized gaussian function
_gauss = lambda x, A, mean, sigma, bgr: A * np.exp(-0.5 * (x - mean) ** 2 / sigma ** 2) / sigma / np.sqrt(
    2 * np.pi) + bgr


def shortprint(values, threshold=6, edgeitems=2):
    """
    Creates a short handy representation string for array values.

    Parameters
    ----------
    values : object
        Values to print.
    threshold: int default 6
        Number of elements to switch to reduced form.
    edgeitems : int default 2
        Items at the edge.

    """
    opt = np.get_printoptions()
    np.set_printoptions(threshold=threshold, edgeitems=edgeitems)
    valuestr = np.array_str(values)
    np.set_printoptions(**opt)
    return valuestr


def _w2f(word):
    """
    Converts strings if possible to float.
    """
    try:
        return float(word)
    except ValueError:
        return word


def parseXML(text):
    root = ElementTree.fromstring(text)
    r = etree_to_dict(root)
    return r


def etree_to_dict(root):
    # d = {root.tag : map(etree_to_dict, root.getchildren())}
    d = {child.attrib['name']: child.text for child in root.iter() if child.text is not None}
    return d


def phase(phases):
    """Transform to [-pi,pi] range."""
    return (phases + np.pi) % (2 * np.pi) - np.pi


# calc peak positions of AgBe
# q=np.r_[0.5:10:0.0001]
# iq=js.sas.AgBeReference(q,data.wavelength[0]/10,n=np.r_[1:15])
# iq.iX[scipy.signal.argrelmax(iq.iY,order=3)[0]]

#: AgBe peak positions
AgBepeaks = [1.0753, 2.1521, 3.2286, 4.3049, 5.3813, 6.4576, 7.5339, 8.6102, 9.6865, 10.7628]


#: Create AgBe peak positions profile
def _agbpeak(q, center=0, fwhm=1, lg=1, asym=0, amplitude=1, bgr=0):
    peak = formel.voigt(x=q, center=center, fwhm=fwhm, lg=lg, asym=asym, amplitude=amplitude)
    peak.Y += bgr
    return peak


# While reading the image file, data are extracted from XML string or text in the EXIF data of the image.
# The following describe what to extract in an line/entry and how to replace:
# 1 name to look for
# 2 the new attribute name (to have later unique names from different detectors)
# 3 a dictionary of char to replace in the line before looking for the keyword/content
# 4 factor to convert to specific units
# 5 return value 'list' or 'string', default list with possible conversion to float
# Not extracted information is in .artist or .imageDescription
exchangekeywords = [['Wavelength', 'wavelength', None, 1, None], ['Flux', 'flux', None, 1, None],
                    ['det_exposure_time', 'exposure_time', None, 1, None],
                    ['det_pixel_size', 'pixel_size', None, 1, None], ['beamcenter_actual', 'beamcenter', None, 1, None],
                    ['detector_dist', 'detector_distance', None, 0.001, None],
                    ['Meas.Description', 'description', None, 1, 'string'], ['wavelength', 'wavelength', None, 1, None],
                    ['Exposure_time', 'exposure_time', None, 1, None],
                    ['Pixel_size', 'pixel_size', {'m': '', 'x ': ''}, 1, None],
                    ['Detector_distance', 'detector_distance', None, 1, None]]


class SubArray(np.ndarray):
    # Defines a generic np.ndarray subclass, that stores some metadata
    # in attributes
    # It seems to be the default way for subclassing maskedArrays
    #  to have the array_finalize from this subclass.

    def __new__(cls, arr):
        x = np.asanyarray(arr).view(cls)
        x.comment = []
        return x

    def __array_finalize__(self, obj):
        if callable(getattr(super(SubArray, self), '__array_finalize__', None)):
            super(SubArray, self).__array_finalize__(obj)
        if hasattr(obj, 'attr'):
            for attribut in obj.attr:
                self.__dict__[attribut] = getattr(obj, attribut)
        try:
            # copy tags from reading
            self._tags = getattr(obj, '_tags')
        except AttributeError:
            pass
        return

    @property
    def array(self):
        return self.view(np.ndarray)

    def setattr(self, objekt, prepend='', keyadd='_'):
        """
        Set (copy) attributes from objekt.

        Parameters
        ----------
        objekt : objekt with attr or dictionary
            Can be a dictionary of names:value pairs like {'name':[1,2,3,7,9]}
            If object has property attr the returned attribut names are copied.
        prepend : string, default ''
            Prepend this string to all attribute names.
        keyadd : char, default='_'
            If reserved attributes (T, mean, ..) are found the name is 'T'+keyadd

        """
        if hasattr(objekt, 'attr'):
            for attribut in objekt.attr:
                try:
                    setattr(self, prepend + attribut, getattr(objekt, attribut))
                except AttributeError:
                    self.comment.append('mapped ' + attribut + ' to ' + attribut + keyadd)
                    setattr(self, prepend + attribut + keyadd, getattr(objekt, attribut))
        elif isinstance(objekt, dict):
            for key in objekt:
                try:
                    setattr(self, prepend + key, objekt[key])
                except AttributeError:
                    self.comment.append('mapped ' + key + ' to ' + key + keyadd)
                    setattr(self, prepend + key + keyadd, objekt[key])

    @property
    def attr(self):
        """
        Show specific attribute names as sorted list of attribute names.

        """
        if hasattr(self, '__dict__'):
            return sorted([key for key in self.__dict__ if key[0] != '_'])
        else:
            return []

    def showattr(self, maxlength=None, exclude=None):
        """
        Show specific attributes with values as overview.

        Parameters
        ----------
        maxlength : int
            Truncate string representation after maxlength char.
        exclude : list of str,default=['comment']
            List of attribute names to exclude from result.

        """
        if exclude is None:
            exclude = ['comment']
        for attr in self.attr:
            if attr not in exclude:
                values = getattr(self, attr)
                # noinspection PyBroadException
                try:
                    valstr = shortprint(values.split('\n'))
                    print('{:>24} = {:}'.format(attr, valstr[0]))
                    for vstr in valstr[1:]:
                        print('{:>25}  {:}'.format('', vstr))
                except:
                    print('%24s = %s' % (attr, str(values)[:maxlength]))

    def __repr__(self):
        # hide that we have a ndarray subclass, just not to confuse people
        return self.view(np.ndarray).__repr__()


subarray = SubArray


# noinspection PyProtectedMember
class Picker:
    def __init__(self, circle, image, destination, symmetry=6):
        self.circle = circle
        self.fig = circle.figure
        self.ax = circle.figure.axes[0]
        self.image = image
        self.iX = image.iX
        self.iY = image.iY
        self.symmetry = symmetry
        self.destination = destination
        self.cidpress = circle.figure.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.cidscroll = circle.figure.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.keypress = circle.figure.canvas.mpl_connect('key_press_event', self.on_keypress)
        self.destination.text(circle.radius, 0.95,
                              'beamcenter \n[{0:.1f}, {1:.1f}]'.format(self.circle.center[1], self.circle.center[0]),
                              fontsize=8)
        self.radialwidth=circle.radius*0.3
        self.update()

    def on_button_press(self, event):
        if event.inaxes is None:
            return
        # print('click', event.xdata,event.ydata)
        self.circle.center = event.xdata, event.ydata
        self.update()

    def on_scroll(self, event):
        if event.inaxes is None:
            return
        if event.button == 'down':
            self.circle.set_radius(self.circle.radius - 1)
        elif event.button == 'up':
            self.circle.set_radius(self.circle.radius + 1)
            self.update()

    def on_keypress(self, event):
        pressedkey = event.key
        # print('-',str(pressedkey), '-')
        if pressedkey == 'up':
            self.circle.center = self.circle.center[0], self.circle.center[1] - 1
        elif pressedkey == 'down':
            self.circle.center = self.circle.center[0], self.circle.center[1] + 1
        elif pressedkey == 'left':
            self.circle.center = self.circle.center[0] - 1, self.circle.center[1]
        elif pressedkey == 'right':
            self.circle.center = self.circle.center[0] + 1, self.circle.center[1]
        elif pressedkey == 'ctrl+up':
            self.circle.center = self.circle.center[0], self.circle.center[1] - 0.1
        elif pressedkey == 'ctrl+down':
            self.circle.center = self.circle.center[0], self.circle.center[1] + 0.1
        elif pressedkey == 'ctrl+left':
            self.circle.center = self.circle.center[0] - 0.1, self.circle.center[1]
        elif pressedkey == 'ctrl+right':
            self.circle.center = self.circle.center[0] + 0.1, self.circle.center[1]
        elif pressedkey == 'u':
            pass
        elif pressedkey == '+':
            self.circle.set_radius(self.circle.radius + 1)
        elif pressedkey == '-':
            self.circle.set_radius(self.circle.radius - 1)
        elif pressedkey == 'ctrl++':
            self.radialwidth+=1
        elif pressedkey == 'ctrl+-':
            self.radialwidth-=1
        self.update()

    def update(self):
        dphi = 2 * np.pi / self.symmetry
        self.image._polarCoordinates([self.circle.center[1], self.circle.center[0]])
        azimuth = self.image._azimuth
        radial = self.image._radial
        awidth = dphi / 2
        image = ndimage.filters.gaussian_filter(self.image.data, 0.8)
        for i, angle in enumerate(np.r_[-np.pi:np.pi:dphi]):
            mask = ((azimuth > (angle - awidth)) & (azimuth < (angle + awidth)) &
                    (radial > self.circle.radius -self.radialwidth) & (radial < self.circle.radius +self.radialwidth))
            # noinspection PyBroadException
            try:
                rad = dA(np.stack([radial[mask], image[mask]]))
                rad.isort()  # sorts along X by default
                # return lower number of points from prune
                result = rad[:, rad.Y > 0].prune(number=50, type='sum', kind='mean')
                result.Y = result.Y /result.Y.max()
                if len(self.destination.lines) > i:
                    # update data
                    self.destination.lines[i].set_xdata(result.X)
                    self.destination.lines[i].set_ydata(result.Y)
                else:
                    # line not yet plotted
                    self.destination.plot(result.X, result.Y)
            except:
                pass
        self.destination.set_xlim(self.circle.radius * 0.7,self.circle.radius * 1.3)
        self.destination.texts[0].set_text(
            'beamcenter \n[{0:.1f}, {1:.1f}]'.format(self.circle.center[1], self.circle.center[0]))
        self.destination.texts[0].set_position([self.circle.radius, 0.95])
        self.fig.canvas.draw()


class sasImage(SubArray, np.ma.MaskedArray):

    def __new__(cls, file, detector_distance=None, beamcenter=None, copy=None, maskbelow=0):
        """
        Creates/reads sasImage as maskedArray from a detector image for evaluation.

        Reads a .tif file including the information in the EXIF tag.
         - All methods of maskedArrays including masking of invalid areas work.
         - Masked areas are automatically masked for all math operations.
         - Arithmetic operations for sasImages work as for numpy arrays
           e.g. to subtract background image or multiplying with transmission.
           Use the numpy.ma methods.
         - Coordinates in images are [height,width] with origin located at upper-left corner.

        Parameters
        ----------
        file : string
            Filename to open.
        detector_distance : float, sasImage
            Detector distance from calibration measurement or calibrated image.
            Overwrites value in the file EXIF tag.
        beamcenter : None, list 2xfloat, sasImage
            Beamcenter is [height, width] position of primary beam with
            origin located at upper-left corner.
            If sasImage is given the corresponding beamcenter is copied.
            Overwrites value given in the file EXIF tag.
        copy : sasImage
            Copy beamcenter, detector_distance, wavelength, pixel_size from image.
            Overwrites data from file, detector_distance and beamcenter.
        maskbelow : float, default =0
            Mask values below this value.

        Returns
        -------
            image : sasImage with attributes
             - .beamcenter : beam center
             - .iX : Height pixel positions
             - .iY : Width pixel positions
             - .filename
             - .artist : Additional attributes from EXIF Tag Artist
             - .imageDescription : Additional attributes from EXIF Tag ImageDescription

        Notes
        -----

        - Unmasked data can be accessed as .data
        - The mask is .mask and initial set to all negative values.
        - Masking of a pixel is done as ``image[i,j]=np.ma.masked``.
          Use mask methods as implemented.
        - Geometry mask methods can be used and additional masking methods from numpy masked Arrays.
          ::

           import jscatter as js
           from numpy import ma
           cal = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
           cal.mask = ma.nomask                  # reset mask
           cal[cal<0]= ma.mask                   # mask negative values
           cal[(cal>30) & (cal<100)] = ma.mask   # mask region of values

        - TIFF tags with index above 700 are ignored.

        - Tested for reading tiff image files from Pilatus detectors as given from our
          metal jet SAXS machines Ganesha and Galaxi at JCNS, Jülich.
        - Additional SAXSpace TIFF files are supported which show frames per pixel on the Y axis.
          This allows to examine the time evolution of the measurement on these line collimation cameras
          (Kratky camera).
          Instead of the old PIL the newer fork Pillow is needed for the multi page TIFFs.
          Additional the pixel_size is set to 0.024 (µm) as for the JCNS CCD camera.
        - Beamcenter & orientation:

          The x,y orientation for images are not well defined and dependent
          on the implementation on the specific camera setup.
          Typically coordinates are used in  [height,width] with the origin in the upper left corner.
          This is opposed to the expectation of [x,y] coordinates with the X horizontal
          and the origin at the lower-left.
          To depict 2D images in the way we expect it from the experimental setup
          (location of the beamcenter, orientation) it is not useful to change orientation.
          Correspondingly the first coordinate (usually expected X) is the height coordinate in vertical direction.
        - For convenient reading of several images:

          - Read calibration measurement as ::

             cal=js.sas.sasImage('mycalibration.tif')

          - Determine detector distance and beamcenter which are stored in calibration sasImage.
          - Read following sasImages using the information stored in sasImage ``cal`` by ::

             sample=js.sas.sasImage('nextsample.tif',detector_distance=cal, beamcenter=cal)


        Examples
        --------
        ::

         import jscatter as js
         #
         # Look at calibration measurement
         calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         # Check beamcenter
         # For correct beamcenter it should show straight lines (change beamcenter to see change)
         calibration.showPolar(beamcenter=[254,122],scaleR=3)
         # or use pickBeamcenter which seems to be more accurate
         calibration.pickBeamcenter()

         # Recalibrate with previous found beamcenter (calibration sets it already)
         calibration.recalibrateDetDistance(showfits=True)
         iqcal=calibration.radialAverage()
         # This might be used to calibrate detector distance for following measurements as
         # empty.setDetectorDistance(calibration)
         #
         empty = js.sas.sasImage(js.examples.datapath+'/emptycell.tiff')
         # Mask beamstop (not the same as calibration, unluckily)
         empty.mask4Polygon([185,92],[190,92],[233,0],[228,0])
         empty.maskCircle(empty.beamcenter, 9)
         empty.show()
         buffer = js.sas.sasImage(js.examples.datapath+'/buffer.tiff')
         buffer.maskFromImage(empty)
         buffer.show()
         bsa = js.sas.sasImage(js.examples.datapath+'/BSA11mg.tiff')
         bsa.maskFromImage(empty)
         bsa.show() # by default a log scaled image
         #
         # subtract buffer (transmission factor is just a guess here, sorry)
         new=bsa-buffer*0.2
         new.show()
         #
         iqempty=empty.radialAverage()
         iqbuffer=buffer.radialAverage()
         iqbsa=bsa.radialAverage()
         #
         p=js.grace(1,1)
         p.plot(iqempty,le='empty cell')
         p.plot(iqbuffer,le='buffer')
         p.plot(iqbsa,le='bsa 11 mg/ml')
         p.title('raw data, no transmission correction')
         p.yaxis(min=1,max=1e3,scale='l',label='I(q) / a.u.')
         p.xaxis(scale='l',label='q / nm\S-1')
         p.legend()

        References
        ----------
        .. [1] Everything SAXS: small-angle scattering pattern collection and correction
               Brian Richard Pauw J. Phys.: Condens. Matter 25,  383201 (2013)
               DOI https://doi.org/10.1088/0953-8984/25/38/383201

        """
        # open file
        if isinstance(file, str):
            # read tiff image
            image = PIL.Image.open(file)
        else:
            # try if this was an opened image
            image = file

        # get EXIF tags
        tags = image.tag_v2 if hasattr(image, 'tag_v2') else image.tag

        try:
            # try im we have multiple frames as for SAXSpace
            # seek(1) returns error for single frame
            image.seek(1)
            image.seek(0)
            if hasattr(PIL, '__version__'):
                # squeeze for single columns
                im = np.asarray([np.asarray(image) for _ii in PIL.ImageSequence.Iterator(image)]).squeeze()
            else:
                raise ImportWarning(
                    'Current version of PIL does not support multi frame images. Install Pillow>=5.2.0 ')

        except EOFError:
            # tif to array conversion for single frame
            # im  = np.asarray(image.transpose(PIL.Image.FLIP_TOP_BOTTOM))
            im = np.asarray(image)
        # set it to writable
        im.flags.writeable = True
        # create the maskedArray from the base class as view
        # create default mask from negative values
        # Pilatus detectors have negative values outside sensitive detector area.
        sub_im = SubArray(im)
        data = np.ma.MaskedArray.__new__(cls, data=sub_im, mask=sub_im < maskbelow)

        # default values
        data.imageDescription = []
        data.artist = []
        data.set_fill_value(0)
        # the EXIF tags contain all meta information.
        # Take them as dictionary and add to artist, imageDescription or respective name from PIL.ExifTags.TAGS.
        data._getEXIF(tags)
        # set attributes from exif and extract some of these data
        data.filename = file
        data.description = '---'
        # keywords to replace
        data._extractAttributes_(exchangekeywords)
        if copy is not None:
            data.setAttrFromImage(copy)
        else:
            if beamcenter is not None:
                data.setBeamcenter(beamcenter)
            if detector_distance is not None:
                data.setDetectorDistance(detector_distance)
        data._issasImage = True
        return data

    def _extractAttributes_(self, attriblist):
        # extract attributes from EXIF entries
        # first words in comments
        firstwords = [line.split()[0] for line in self.imageDescription + self.artist if len(line.strip()) > 0]
        for attribs in attriblist:
            if attribs[0] in firstwords:
                self.getfromcomment(attribs[0], replace=attribs[2], newname=attribs[1])
                if attribs[4] == 'string':
                    setattr(self, attribs[1], ' '.join([str(v) for v in getattr(self, attribs[1])]))
                else:
                    setattr(self, attribs[1],
                            [v * attribs[3] if isinstance(v, (float, int)) else v for v in getattr(self, attribs[1])])

    # noinspection PyBroadException
    def _getEXIF(self, tags):
        # Take them as dictionary and add to artist, imageDescription or respective name from PIL.ExifTags.TAGS.
        self._tags = tags
        # extract EXIF data and save them in artist and imageDescription
        for k, v in dict(self._tags).items():
            if k > 700:
                continue
            elif k == 270:
                # TAGS[270] = 'ImageDescription'
                # from Galaxy or Ganesha
                self.setattr(
                    {'imageDescription': [vv[1:].strip() if vv[0] == '#' else vv.strip() for vv in v.splitlines()]})
            elif k == 315:
                # TAGS[315] =  'Artist'
                # in XML tag from Ganesha. Throws error if not a XML tag as for Galaxy
                try:
                    self.entriesXML = parseXML(self._tags[315])
                    self.setattr({'artist': [str(k) + ' ' + str(v) for k, v in self.entriesXML.items()]})
                except ElementTree.ParseError:
                    if isinstance(self._tags[315], basestring):
                        # catch if it is a single string as for SAXSPACE
                        self.setattr({'artist': [self._tags[315]]})
                    else:
                        self.setattr({'artist': []})
            else:
                if k in PIL.ExifTags.TAGS:
                    self.setattr({PIL.ExifTags.TAGS[k]: v if isinstance(v, (list, set)) else [v]})
        try:
            if self.artist[0] == 'Anton Paar GmbH':
                # catches SAXSPACE TIFF files
                # iv are specific for SAXSPACE
                for k, iv in dict({'wavelength': 65024, 'detector_distance': 65060}).items():
                    v = self._tags[iv]
                    self.setattr({k: v if isinstance(v, (list, set)) else [v]})
                self.pixelSize = 0.024  # 24 µm
        except:
            pass

        return

    def _setEXIF(self):
        # set Exif entries according to attributes if these were changed
        # see PIL.TiffTags.TYPES for types
        # we add anything new to TAGS[270]
        for k, v in dict(self._tags).items():
            if k > 700:
                continue
            elif k == 270:
                # TAGS[270] = 'ImageDescription'
                content = ['processed by Jscatter']
                content += self.imageDescription
                for ekw in exchangekeywords:
                    # noinspection PyBroadException
                    try:
                        content.append(ekw[0] + ' ' + ' '.join([str(a) for a in getattr(self, ekw[1])]))
                    except:
                        pass
                self._tags[k] = '\n'.join(content)
            elif k == 315:
                # TAGS[315] = 'Artist'
                self._tags[k] = '\n'.join(self.artist)
            else:
                if k in PIL.ExifTags.TAGS:
                    content = getattr(self, PIL.ExifTags.TAGS[k])[0]
                    type = self._tags.tagtype[k]
                    if type == 2:
                        self._tags[k] = ' '.join(content)
                    elif type in [3, 4, 8, 9]:
                        self._tags[k] = content
                    else:
                        self._tags[k] = content
        return

    @property
    def iY(self):
        """
        Y pixel coordinates

        """
        return np.repeat(np.r_[0:self.shape[1]][None, :], self.shape[0], axis=0)

    @property
    def iX(self):
        """
        X pixel coordinates

        """
        return np.repeat(np.r_[0:self.shape[0]][:, None], self.shape[1], axis=1)

    @property
    def array(self):
        """
        Strip of all attributes and return a simple array without mask.
        """
        return self.data.array

    def __repr__(self):
        beamcenter = self.beamcenter if hasattr(self, 'beamcenter') else None
        detector_distance = self.detector_distance if hasattr(self, 'detector_distance') else None

        desc = "sasImage-> \n{0} \nbeamcenter={1} \ndetector distance={2} \nshape={3} "
        return desc.format(self, beamcenter, detector_distance, self.shape)

    def getfromcomment(self, name, replace=None, newname=None):
        """
        Extract name from .artist or .imageDescription with attribute name in front.

        If multiple names start with parname first one is used.
        Used line is deleted from .artist or .imageDescription.

        Parameters
        ----------
        name : string
            Name of the parameter in first place.
        replace : dict
            Dictionary with pairs to replace in all lines.
        newname : string
            New attribute name

        """
        if newname is None:
            newname = name
        # first look in imageDescription
        for i, line in enumerate(self.imageDescription):
            if isinstance(replace, dict):
                for k, v in replace.items():
                    line = line.replace(k, str(v))
            words = line.split()
            if len(words) > 0 and words[0] == name:
                setattr(self, newname, [_w2f(word) for word in words[1:]])
                del self.imageDescription[i]
                return
        # then in artist
        for i, line in enumerate(self.artist):
            if isinstance(replace, dict):
                for k, v in replace.items():
                    line = line.replace(k, str(v))
            words = line.split()
            if len(words) > 0 and words[0] == name:
                setattr(self, newname, [_w2f(word) for word in words[1:]])
                del self.artist[i]
                return

    def setDetectorDistance(self, detector_distance, offset=0):
        """
        Set detector distance from calibration .

        Parameters
        ----------
        detector_distance : float, sasImage
            New value for detector distance.
            If sasImage the detector_distance is copied.
        offset : float
            Offset for sample compared to calibration sample.


        """
        if isinstance(detector_distance, (float, int)):
            self.detector_distance = [detector_distance + offset]
        elif isinstance(detector_distance, (list, set)):
            self.detector_distance = [v + offset if isinstance(v, (float, int)) else v for v in detector_distance]
        elif isinstance(detector_distance, sasImage):
            self.detector_distance = [v + offset if isinstance(v, (float, int)) else v
                                      for v in detector_distance.detector_distance]

    def setBeamcenter(self, beamcenter):
        """
        Set beamcenter .

        Parameters
        ----------
        beamcenter : float, sasImage
            New value for beamcenter as [height, width].
            If sasImage the beamcenter is copied.


        """
        if hasattr(beamcenter, 'beamcenter'):
            self.beamcenter = list(beamcenter.beamcenter)
        else:
            # copy from object
            self.beamcenter = list(beamcenter)

    def setAttrFromImage(self, image):
        """
        Copy beamcenter, detector_distance, wavelength, pixel_size from image.

        Parameters
        ----------
        image  sasImage
            sasImage to copy attributes to self.


        """
        self.setBeamcenter(image)
        self.setDetectorDistance(image)
        self.pixel_size=copy.copy(image.pixel_size)
        self.wavelength=copy.copy(image.wavelength)

    def pickBeamcenter(self, levels=8, symmetry=6):
        """
        Open image to pick the beamcenter from a calibration sample as AgBe.

        Radial averaged sectors allow to find the optimal beamcenter with best overlap of peaks.
        Closing the image accepts the actual selected beamcenter.

        Parameters
        ----------
        levels : int
            Number of levels in contour image.
        symmetry : int
            Number of sectors around beamcenter for radial averages.

        Returns
        -------
            After closing the selected beamcenter is saved in the sasImage.

        Notes
        -----
        A figure with the AgBe picture (right) and a radial average over sectors is shown
        (left, symmetry defines number of sectors) .

        - A circle is shown around the mouse point after clicking. By default the radius corresponds to an AgBe reflex.
          The radius can be changed by mouse wheel or +/- keys.
        - Radius of the circle (center of left plot data) can be increased/decreased by +/-.
        - Width around radius can be increased/decrease by ctrl++/ctrl+-.
        - The beamcenter can be changed by the mouse pointer (click).
        - The beamcenter can be moved by arrow keys (+-1) or ctrl+arrow (+-0.1)
        - In the sectors a radial average (after some smoothing) is calculated and shown in the left axes.
        - The beamcenter is OK if the peaks show maximum overlap.


         Examples
         --------
         ::

          import jscatter as js
          #
          calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
          # use pickBeamcenter
          calibration.pickBeamcenter()


        """
        colorMap = 'jet'
        origin = 'lower'
        fontsize = 10
        extend = None

        wl = self.wavelength[0] / 10.  # conversion to nm
        dd = self.detector_distance[0]
        # pixel r from q
        pfq = lambda q: dd * np.tan(2 * np.arcsin(np.asarray(q) * wl / 4. / np.pi))
        pixelpeaks = pfq(AgBepeaks) / self.pixel_size[0]
        # guess good AgBe peak
        pixelradius = pixelpeaks[np.abs(pixelpeaks - np.min(self.shape) / 5).argmin()]

        fig = pyplot.figure()
        ax1 = fig.add_axes([0.4, 0.05, 0.6, 0.85])
        ax0 = fig.add_axes([0.1, 0.1, 0.3, 0.8])
        cmap = pyplot.get_cmap(colorMap)
        lmap = pyplot.get_cmap(None)
        fig.suptitle(
            'Move beamcenter: Pick with mouse; Close to accept \narrows(+-1 pixel) or ctrl+arrow (+-0.1 pixel) ',
            fontsize=10)
        ax1.yaxis.tick_right()
        ax1.yaxis.set_label_position("right")
        logself = np.ma.log(self)
        im = ax1.imshow(logself, cmap=cmap, extent=extend, origin=origin)
        im.cset = ax1.contour(logself, levels=levels, linewidths=1, cmap=lmap, extent=extend, origin=origin)
        im.labels = ax1.clabel(im.cset, inline=True, fmt='%1.1f', fontsize=fontsize)
        fig.colorbar(im, ax=ax1, orientation='horizontal', shrink=0.7, fraction=0.03,
                     pad=0.1)  # note that colorbar is a method of the figure, not the axes
        ax1.invert_yaxis()
        ax1.set_xlabel('Y dimension / pixel')
        ax1.set_ylabel('X dimension / pixel')
        ax0.set_xlabel('radius / pixel')
        ax0.set_ylabel('normalized mean count rate / pixel')

        # create circle and add it to figure
        if hasattr(self, 'beamcenter'):
            center = [self.beamcenter[1], self.beamcenter[0], ]
            print('Old position of beamcenter: [{0:.2f},{1:.2f}]'.format(center[1], center[0]))
        else:
            center = (self.shape[1] / 2, self.shape[0] / 2)
            print('No beamcenter defined')
        circle = Circle(center, pixelradius, color='k', fill=False, linewidth=2,
                        linestyle=(0, (6, 3)))  # np.min(self.shape)/3

        ax1.add_artist(circle)
        # create picker and turn matplotlib to blocking mode to wait until window is closed
        pick = Picker(circle=circle, image=self, destination=ax0, symmetry=symmetry)
        mpl.pyplot.show(block=True)
        # now set beamcenter
        self.setBeamcenter([pick.circle.center[1], pick.circle.center[0]])
        print('Set beamcenter to [{0:.2f},{1:.2f}]'.format(self.beamcenter[0], self.beamcenter[1]))

    def maskReset(self):
        """
        Reset the mask.

        By default values smaller 0 are automatically masked again as is also default for reading

        """
        self.mask=ma.nomask
        self[self<0] = ma.masked

    def maskFromImage(self, image):
        """
        Use/copy mask from image.

        Parameters
        ----------
        image : sasImage
            sasImage to use mask for resetting mask.
            image needs to have same dimension.

        """
        if image.shape == self.shape:
            self.mask = image.mask

    def maskRegion(self, xmin, xmax, ymin, ymax):
        """
        Mask rectangular region.

        Parameters
        ----------
        xmin,xmax,ymin,ymax : int
            Corners of the region to mask

        """
        self[xmin:xmax, ymin:ymax] = ma.masked

    def maskRegions(self, regions):
        """
        Mask several regions.

        Parameters
        ----------
        regions : list
            List of regions as in maskRegion.

        """
        for region in regions:
            self.maskRegion(*region)

    def maskbelowLine(self, p1, p2):
        """
        Mask points at one side of line.

        The masked side is left looking from p1 to p2.

        Parameters
        ----------
        p1, p2 : list of 2x float
            Points in pixel coordinates defining line.


        """
        points = np.stack([self.iX, self.iY])
        pp1 = np.array(p1)
        pp2 = np.array(p2)
        d = np.cross((pp1 - pp2)[:, None, None], pp2[:, None, None] - points, axis=0)
        self[d > 0] = ma.masked

    def maskTriangle(self, p1, p2, p3, invert=False):
        """
        Mask inside triangle.

        Parameters
        ----------
        p1,p2,p3 : list of 2x float
            Edge points of triangle.
        invert : bool
            Invert region. Mask outside circle.

        """
        points = np.stack([self.iX, self.iY], axis=2)
        pp1 = np.array(p1)
        pp2 = np.array(p2)
        pp3 = np.array(p3)
        # cross to get sides of lines
        d1 = np.sign(
            np.cross((pp1 - pp2)[None, None, :], points - pp2[None, None, :], axis=2).reshape(points.shape[0], -1))
        d2 = np.sign(
            np.cross((pp2 - pp3)[None, None, :], points - pp3[None, None, :], axis=2).reshape(points.shape[0], -1))
        d3 = np.sign(
            np.cross((pp3 - pp1)[None, None, :], points - pp1[None, None, :], axis=2).reshape(points.shape[0], -1))
        # equal side if sign equal sign of 3rd point
        mask = ((d1 == d1[p3[0], p3[1]]) & (d2 == d2[p1[0], p1[1]]) & (d3 == d3[p2[0], p2[1]]))
        if invert:
            self[~mask] = ma.masked
        else:
            self[mask] = ma.masked

    def mask4Polygon(self, p1, p2, p3, p4, invert=False):
        """
        Mask inside polygon of 4 points.

        Points need to be given in right hand order.

        Parameters
        ----------
        p1,p2,p3,p4 : list of 2x float
            Edge points.
        invert : bool
            Invert region. Mask outside circle.

        """
        points = np.stack([self.iX, self.iY], axis=2)
        pp1 = np.array(p1, dtype=np.int32)
        pp2 = np.array(p2, dtype=np.int32)
        pp3 = np.array(p3, dtype=np.int32)
        pp4 = np.array(p4, dtype=np.int32)
        # cross to get sides of lines
        d1 = np.sign(
            np.cross((pp1 - pp2)[None, None, :], points - pp2[None, None, :], axis=2).reshape(points.shape[0], -1))
        d2 = np.sign(
            np.cross((pp2 - pp3)[None, None, :], points - pp3[None, None, :], axis=2).reshape(points.shape[0], -1))
        d3 = np.sign(
            np.cross((pp3 - pp4)[None, None, :], points - pp4[None, None, :], axis=2).reshape(points.shape[0], -1))
        d4 = np.sign(
            np.cross((pp4 - pp1)[None, None, :], points - pp1[None, None, :], axis=2).reshape(points.shape[0], -1))
        # equal side if sign equal sign of 3rd point
        mask = ((d1 == d1[pp3[0], pp3[1]]) & (d2 == d2[pp4[0], pp4[1]]) & (d3 == d3[pp1[0], pp1[1]]) & (
                    d4 == d3[pp2[0], pp2[1]]))
        if invert:
            self[~mask] = ma.masked
        else:
            self[mask] = ma.masked

    def maskCircle(self, center, radius, invert=False):
        """
        Mask points inside circle.

        Parameters
        ----------
        center : list of 2x float
            Center point.
        radius : float
            Radius in pixel units
        invert : bool
            Invert region. Mask outside circle.


        """
        points = np.stack([self.iX, self.iY])
        distance = la.norm(points - np.array(center)[:, None, None], axis=0)
        mask = distance < radius
        if invert:
            self[~mask] = ma.masked
        else:
            self[mask] = ma.masked

    def maskSectors(self, angles, width, radialmax=None, beamcenter=None, invert=False):
        """
        Mask sector around beamcenter.

        Zero angle is

        Parameters
        ----------
        angles : list of float
            Center angles of sectors in grad.
        width : float or list of float
            Width of the sectors in grad.
            If single value all sectors are equal.
        radialmax : float
            Maximum radius in pixels.
        beamcenter : 2x float
            Center if different from stored beamcenter.
        invert : bool
            Invert mask or not.

        Examples
        --------
        ::

         import jscatter as js
         cal = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         cal.maskSectors([0,90,180],20,radialmax=100,invert=True)
         cal.show()

        """
        if beamcenter is None:
            beamcenter = self.beamcenter
        self._polarCoordinates(beamcenter)
        angles = np.asarray(angles)

        if isinstance(width, (float, int)):
            width = np.ones_like(angles) * width

        mask = self.mask.copy()
        mask[:] = False

        for a, w in zip(np.deg2rad(angles), np.deg2rad(np.abs(width))):
            limits = np.r_[a - w / 2, a + w / 2] % (2 * np.pi) - np.pi
            if radialmax is None:
                if limits[0] < limits[1]:
                    mask = np.logical_or(mask, (self._azimuth > limits[0]) & (self._azimuth < limits[1]))
                else:
                    mask = np.logical_or(mask, ~((self._azimuth < limits[0]) & (self._azimuth > limits[1])))
            else:
                if limits[0] < limits[1]:
                    mask = np.logical_or(mask, (self._azimuth > limits[0]) & (self._azimuth < limits[1]) & (
                                self._radial < radialmax))
                else:
                    mask = np.logical_or(mask, ~((self._azimuth < limits[0]) & (self._azimuth > limits[1])) & (
                                self._radial < radialmax))
        if invert:
            self[~mask] = ma.masked
        else:
            self[mask] = ma.masked

    def findCenterOfIntensity(self, beamcenter=None, size=100):
        """
        Find beam center as center of intensity around beamcenter.

        Only values above the mean value are used to calc center of intensity.
        Use an image with a clear symmetric and  strong scattering sample as AgBe.
        Use *.showPolar([600,699],scaleR=5)* to see if peak is symmetric.

        Parameters
        ----------
        beamcenter : list 2x int
            First estimate of beamcenter as [height, width] position.
            If not given preliminary beamcenter is estimated as center of intensity of full image.
        size : int
            Defines size of rectangular region of interest (ROI) around the beamcenter to look at.

        Returns
        -------
            Adds (replaces) .beamcenter as attribute.

        Notes
        -----
        If ROI is to large the result may be biased due to asymmetry of
        the intensity distribution inside of ROI.

        """
        if isinstance(size, float):
            size = np.rint(size).astype(np.int)
        med = (self.max() + self.min()).array / 2.
        if beamcenter is None:
            # as first guess
            beamcenter = ndimage.measurements.center_of_mass(ma.masked_less(self, med, copy=True).filled(0).array)
        if size is not None:
            # take smaller portion to reduce bias from image size
            bc = np.rint(beamcenter).astype(np.int)
            data = self[bc[0] - size:bc[0] + size, bc[1] - size:bc[1] + size]
            # mask values smaller than mean and take centerofmass
            med = (data.max() + data.min()).array / 2.
            center = ndimage.measurements.center_of_mass(ma.masked_less(data, med, copy=True).filled(0).array)
            beamcenter = [center[0] + bc[0] - size, center[1] + bc[1] - size]
        self.setBeamcenter(beamcenter)

    def _findCenterAgBe(self, beamcenter=None, size=40):
        """
        Currently not working!!

        Find beamcenter as center of Debye-Scherrer rings of AgBe powder.

        Parameters
        ----------
        beamcenter : 2x int
            Estimate of center.
            If not given findCenterOfIntensity is used to estimate center.
        size : int
            Rectangular region around the beamcenter to look at.

        Returns
        -------
            Adds .beamcenter as attribute.

        """
        if beamcenter is None:
            if not hasattr(self, 'beamcenter'):
                self.findCenterOfIntensity(size=size)
                print('Found new beamcenter at ', self.beamcenter)
            else:
                print('Use beamcenter at ', self.beamcenter)
            beamcenter = self.beamcenter
        # get original mask
        orgmask = self.mask
        X = self.iX - beamcenter[0]
        Y = self.iY - beamcenter[1]
        mean = self.mean()

        # calc approximate radial wavevectors in real coordinates
        xxyy = ((X * self.pixel_size[0]) ** 2 + (Y * self.pixel_size[1]) ** 2) ** 0.5
        phi = np.arctan2(X, Y)
        # scattering angle
        angle = np.arctan(xxyy / self.detector_distance[0])
        wl = self.wavelength[0] / 10.  # conversion to nm
        q = 4 * np.pi / wl * np.sin(angle / 2)
        dq = 0.3  # around peak positions

        nn = 20
        dphi = np.pi / nn
        # bc = []
        # AgBepeaks contains a list of AgBe peak positions to test for
        print(beamcenter)
        for agp in AgBepeaks:
            qmask = (q > agp - dq) & (q < agp + dq)
            centers = []
            print('-----------------------------------')
            for i, a1 in enumerate(np.r_[0:nn] * dphi):
                # symmetric side is -pi
                a2 = a1 - np.pi
                # make masks
                pi1 = qmask & ((phi > a1) & (phi < (a1 + dphi))) & ~orgmask
                pi2 = qmask & ((phi > a2) & (phi < (a2 + dphi))) & ~orgmask
                # only proceed if sizes of both sides are equal (no mask involved)
                # print('#1 ',a1,pi1.sum(),a2,pi2.sum() )
                if pi1.sum() == pi2.sum() and pi1.sum() > 10:
                    # only above mean
                    pi1max = pi1 & (self > mean)
                    # X and Y mean
                    Xpi1mean = np.mean(X[pi1max].astype(np.float64))  # * self[pi1max]) / self[pi1max].sum()
                    Ypi1mean = np.mean(Y[pi1max].astype(np.float64))  # * self[pi1max]) / self[pi1max].sum()
                    # same for other side
                    pi2max = pi2 & (self > mean)
                    Xpi2mean = np.mean(X[pi2max].astype(np.float64))  # * self[pi2max]) / self[pi2max].sum()
                    Ypi2mean = np.mean(Y[pi2max].astype(np.float64))  # * self[pi2max]) / self[pi2max].sum()
                    centers.append([(Xpi1mean + Xpi2mean) / 2, (Ypi1mean + Ypi2mean) / 2, abs(Xpi1mean - Xpi2mean),
                                    abs(Ypi1mean - Ypi2mean)])
                    print('pi1 ', ["%0.2f" % i for i in [pi1.sum(), Xpi1mean, Ypi1mean, Xpi2mean, Ypi2mean]])
            if len(centers) > nn * 0.7:
                centers = np.array(centers).T
                # use only better 45 degree
                choose = (centers[2] / (centers[2] ** 2 + centers[3] ** 2) ** 0.5) > 0.5 ** 0.5
                bc = [np.mean(centers[0, ~choose]), np.mean(centers[1, choose])]
                print(bc)
        # self.beamcenter= centers
        print(centers)
        # restore original mask
        self.mask = ma.nomask
        self[orgmask] = ma.masked

    def radialAverage(self, beamcenter=None, number=300, kind='log'):
        """
        Radial average of image and conversion to wavevector q.

        Remember to set .detector_distance to calibrated value.

        Parameters
        ----------
        beamcenter : list 2x float
            Sets beam center or radial center in data and uses this.
            If not given the attribut beamcenter in the data is used.
        number : int, default 500
            Number of intervals on new X scale.
        kind : 'lin', default 'log'
            Determines how points are distributed.

        Returns
        -------
            dataArray

        Notes
        -----

        - Correction of pixel size for flat detector projected to Ewald sphere included.
        - The value in a q binning is the average count rate :math:`c(q)=(\sum c_i)/N`
          with counts in pixel *i* :math:`c_i` and number of pixels :math:`N`
        - The error (standard deviation) is calculated in a q binning as
          :math:`e=(\sum c_i)^{1/2}/N`
        - The error is valid for single photon counting detectors showing Poisson statistics
           as the today typical Pilatus detectors from DECTRIS.


        Examples
        --------
        Mask and do radial average over sectors. ::

         import jscatter as js
         cal = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         p=js.grace()
         calc=cal.copy()
         calc.maskSectors([0,180],20,radialmax=100,invert=True)
         calc.show()
         icalc=calc.radialAverage()
         p.plot(icalc,le='horizontal')
         calc=cal.copy()
         calc.maskSectors([90+0,90+180],20,radialmax=100,invert=True)
         calc.show()
         icalc=calc.radialAverage()
         p.plot(icalc,le='vertical')
         p.yaxis(scale='l')
         p.legend()
         p.title('The AgBe is not isotropically ordered')


        """
        if beamcenter is not None:
            self.setBeamcenter(beamcenter)
        X = (self.iX - self.beamcenter[0]) * self.pixel_size[0]
        Y = (self.iY - self.beamcenter[1]) * self.pixel_size[1]
        # calc radial wavevectors
        r = np.linalg.norm([X, Y], axis=0)
        angle = np.arctan(r / self.detector_distance[0])
        wl = self.wavelength[0] / 10.  # conversion to nm
        self.q = 4 * np.pi / wl * np.sin(angle / 2)
        # correction for flat detector with pixel area
        lpl0 = 1. / np.cos(angle)
        data = self.data * lpl0 ** 3
        mask = self.mask
        radial = dA(np.stack([self.q[~mask], data[~mask]]))
        radial.isort()  # sorts along X by default
        # return lower number of points from prune
        result = radial.prune(number=number, type='sum', kind=kind)  # average without error
        err = result[1] ** 0.5
        result[1] = result[1] /result[2]  # mean
        result[2] = err / result[2]  # mean error
        result.setColumnIndex(iey=2)
        result.filename = self.filename
        # add some attributes from image
        for attri in ['DateTime', 'ImageLength', 'ImageWidth', 'XResolution', 'YResolution', 'beamcenter',
                      'description', 'detector_distance', 'exposure_time', 'filename', 'imageDescription',
                      'pixel_size', 'wavelength']:
            try:
                setattr(result, attri, getattr(self, attri))
            except AttributeError:
                pass

        return result

    @staticmethod
    def _qfrompixel(r, wl, dd):
            #: q from pixel position
            return 4 * np.pi / wl * np.sin(0.5 * np.arctan(r / dd))

    def getPixelQ(self):
        """
        Get scattering vector along pixel dimension around beamcenter.

        Needs wavelength, detector_distance and beamcenter defined.

        Returns
        -------
            qx,qy with image x and y dimension

        """
        try:
            wl = self.wavelength[0] / 10.  # conversion to nm
            dd = self.detector_distance[0]
            # pixel distances
            X = (np.r_[0:self.shape[0]] - self.beamcenter[0]) * self.pixel_size[0]
            Y = (np.r_[0:self.shape[1]] - self.beamcenter[1]) * self.pixel_size[1]
        except AttributeError:
            print('You may set wavelength, detector_distance and beamcenter manually !!')
            raise

        return self._qfrompixel(X, wl, dd), self._qfrompixel(Y, wl, dd)

    def lineAverage(self, beamcenter=None, number=None, minmax='auto', show=False):
        """
        Line average of image and conversion to wavevector q for line collimation cameras.

        Remember to set .detector_distance to calibrated value.

        Parameters
        ----------
        beamcenter : float
            Sets beam center in data and uses this.
            If not given the beam center is determined from semitransparent beam.
        number : int, default None
            Number of intervals on new X scale. None means all pixels.
        minmax : [int,int], 'auto'
            Interval for determination of beamcenter.
        show : bool
            Show the fit of the primary beam.

        Returns
        -------
            dataArray
             - .filename
             - .detector_distance
             - .description
             - .beamcenter

        Notes
        -----
        - Detector distance in attributes is used.
        - The primary beam is automatically detected.
        - Correction for flat detector projected to Ewald sphere included.

        """
        if beamcenter is None:
            # take average
            imageav = dA(np.c_[np.r_[0:self.shape[0]], self.mean(axis=1)].T)
            # find minima from argmax if not given explicitly
            if minmax[0] == 'a':  # auto
                # for normal empty cell or buffer measurement the primary beam is the maximum
                imax = imin = imageav.Y.argmax()
                while imageav.Y[imax + 1] < imageav.Y[imax]:      imax += 1
                while imageav.Y[imin - 1] < imageav.Y[imin]:      imin -= 1
                xmax = imageav.X[imax]
                xmin = imageav.X[imin]
            else:
                xmin = minmax[0]
                xmax = minmax[1]
            # prune to smaller interval
            primarybeam = imageav.prune(lower=xmin, upper=xmax)
            # subtract min value , which is basically dark current
            primarybeam.Y -= primarybeam.Y.min()
            norm = scipy.integrate.simps(primarybeam.Y, primarybeam.X)
            primarybeam.Y = primarybeam.Y /norm
            # fit mean position and width
            primarybeam.fit(_gauss, {'mean': imageav.Y.argmax(), 'sigma': 0.015, 'bgr': 0, 'A': 1}, {}, {'x': 'X'})
            beamcenter = primarybeam.mean
            self.primarybeam_hwhm = primarybeam.sigma * np.sqrt(np.log(2.0))
            self.primarybeam_peakmax = primarybeam.modelValues(x=primarybeam.mean).Y[0] * norm
            if show:
                primarybeam.showlastErrPlot()
        self.beamcenter = beamcenter
        r = (self.iX[0] - self.beamcenter) * self.pixelSize  # µm pixel size
        # calc radial wavevectors
        angle = np.arctan(r / self.detector_distance[0])
        wl = self.wavelength[0]
        self.q = 4 * np.pi / wl * np.sin(angle / 2)
        # correction for flat detector with pixel area
        lpl0 = 1. / np.cos(angle)
        data = self.mean(axis=0) * lpl0  # because of line collimation only power 1
        error = self.std(axis=0) * lpl0  # because of line collimation only power 1
        result = dA(np.stack([self.q, data, error]))
        if number is not None:
            # return lower number of points from prune
            result = result.prune(number=number, kind='mean+')  # makes averages with errors
        result.filename = self.filename
        result.detector_distance = self.detector_distance
        result.description = self.description
        return result

    def recalibrateDetDistance(self, beamcenter=None, number=500, showfits=False):
        """
        Recalibration of detectorDistance by AgBe reference for point collimation.

        Use only for AgBe reference measurements to determine the correction factor.
        For non AgBe measurements set during reading or .detector_distance to the new value.
        May not work if the detector distance is totally wrong.

        Parameters
        ----------
        beamcenter : list 2x float
            Sets beam center or radial center in data and uses this.
            If not given the attribut beamcenter in the data is used.
        number : int, default 1000
            number of intervals on new X scale.
        showfits : bool
            Show the AgBe peak fits.


        Notes
        -----
        - .distanceCorrection will contain factor for correction.
          Repeating this results in a .distanceCorrection close to 1.

        """
        # do radial average
        iq = self.radialAverage(beamcenter=beamcenter, number=number)
        # later distance corrections
        self.distanceCorrection = []
        dq = 0.3  # around peak positions
        for agp in AgBepeaks:
            # AgBepeaks contains a list of AgBe peak positions to test for
            # we fit each with a voigt function and take later the average
            if iq.X.max() > agp + dq and iq.X.min() < agp - dq:
                # cut between lower and upper and fit Voigt function for peak
                iqq = iq.prune(lower=agp - dq, upper=agp + dq, weight=None)
                # iqq.setColumnIndex(iey=None)
                if iqq.shape[1] < 5:
                    continue
                iqq.setLimit(amplitude=[0], bgr=[0], fwhm=[0.001, agp])
                ret = iqq.fit(_agbpeak, {'center': agp, 'amplitude': iqq.Y.max() / 4.,
                                         'fwhm': 0.1, 'asym': 1, 'bgr': iqq.Y.min() / 2.},
                              {}, {'q': 'X'}, output=False)
                if ret == -1:
                    continue
                if showfits:
                    iqq.showlastErrPlot()
                self.distanceCorrection += [iqq.center / agp]
        corfactor = np.mean(self.distanceCorrection)
        corstd = np.std(self.distanceCorrection) / corfactor
        # set new detectorDistance
        self.detector_distance[0] *= corfactor
        print('\nCorrection factor {0:.4f} to new distance {1:.4f} (rel error : {2:.4f} )'.
              format(corfactor, self.detector_distance[0], corstd))

    def show(self, **kwargs):
        """
        Show sasImage as matplotlib figure.

        Parameters
        ----------
        scale : 'log', 'symlog', default = 'norm'
            Scale for intensities.

            - 'norm' Linear scale.
            - 'log' Logarithmic scale
            - 'symlog' Symmetrical logarithmic scale is logarithmic in both the positive
              and negative directions from the origin. This works also for only positive data.
              Use linthresh, linscale to adjust.
        levels : int, None
            Number of contour levels.
        colorMap : string
            Get a colormap instance from name.
            Standard mpl colormap name (see showColors).
        linthresh : float, default = 1
            Only used for scale 'symlog'.
            The range within which the plot is linear (-linthresh to linthresh).
        linscale : float, default = 1
            Only used for scale 'symlog'.
            Its value is the number of decades to use for each half of the linear range.
            E.g. 10 uses 1 decade.
        lineMap : string
            Label color
            Colormap name as in colorMap, otherwise as cs in in Axes.clabel
            * if None, the color of each label matches the color of the corresponding contour
            * if one string color, e.g., colors = ‘r’ or colors = ‘red’, all labels will be plotted in this color
            * if a tuple of matplotlib color args (string, float, rgb, etc),
              different labels will be plotted in different colors in the order specified
        fontsize : int, default 10
            Size of line labels in pixel
        title : None, string
            Title of the plot.
            May be set by fig.axes[0].set_title('title')
        axis : None, 'pixel'
            If coordinates should be forced to pixel, otherwise wavevectors if possible.
        invert_yaxis, invert_xaxis : bool
            Invert corresponding axis.
        block : bool
            Open in blocking or non-blocking mode
        origin : 'lower','upper'
            Origin of the plot. See matplotlib imshow.

        Returns
        -------
            image handle

        Examples
        --------
        Use radial averaged data to interpolate ::

         import jscatter as js
         import numpy as np
         calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         calibration.show(colorMap='ocean')
         calibration.show(scale='sym',linthresh=20, linscale=5)

        Use ``scale='symlog'`` for mixed lin-log scaling to pronounce low scattering.
        See mpl.contourImage for more options also available using ``.show``. ::

         import jscatter as js
         import numpy as np
         # sets negative values to zero
         bsa = js.sas.sasImage(js.examples.datapath+'/BSA11mg.tiff')
         fig=js.mpl.contourImage(bsa,scale='sym',linthresh=30, linscale=10)
         fig.axes[0].set_xlabel(r'$Q_{{ \mathrm{{X}} }}\;/\;\mathrm{{nm^{{-1}}}}$ ')
         fig.axes[0].set_ylabel(r'$Q_{{ \mathrm{{Y}} }}\;/\;\mathrm{{nm^{{-1}}}}$ ')

        """
        block=kwargs.pop('block', False)
        kwargs.update({'invert_yaxis': True, 'block': False})

        axis = kwargs.pop('axis', None)
        if axis != 'pixel':
            try:
                # if wavevectors are working we name them
                _ = self.getPixelQ()
                unit = r'$Q_{{ \mathrm{{ {0:s}}} }}\;/\;\mathrm{{nm^{{-1}}}}$ '
            except AttributeError:
                unit = '{0:s} pixel'
                kwargs.update({'axis': 'pixel'})
        else:
            unit = '{0:s} pixel'
            kwargs.update({'axis': 'pixel'})

        fig = mpl.contourImage(x=self, **kwargs)

        fig.axes[0].set_xlabel(unit.format('Y'))
        fig.axes[0].set_ylabel(unit.format('X'))
        mpl.pyplot.show(block=block)
        return fig

    def gaussianFilter(self, sigma=2):
        """
        Gaussian filter in place.

        Uses ndimage.filters.gaussian_filter with default parameters except sigma.

        Parameters
        ----------
        sigma : float
            Gaussian kernel sigma.

        """
        self[self.mask] = ndimage.filters.gaussian_filter(self.data, sigma)[self.mask]

    def reduceSize(self, pixelsize=2, center=None, border=None):
        """
        Reduce size of image using uniform average in box.

        XResolution,YResolution,beamcenter are scaled correspondingly.

        Parameters
        ----------
        pixelsize : int
            Pixel size of the box to average.
            Also factor for reduction.
        center : [int,int]
            Center of crop region.
        border : int
            Size of crop region.
             - If center is given a box with 2*size around center is used.
             - If center is None the border is cut by size.

        Returns
        -------
            sasImage

        """
        i1 = i3 = 0
        i2 = i4 = 100000

        if border is not None:
            # set box around center or from border
            if center is not None:
                center = np.asarray(center, int)
                i1 = center[0] - border
                i2 = center[0] + border
                i3 = center[1] - border
                i4 = center[1] + border
            else:
                i1 = border
                i2 = self.shape[0] - border
                i3 = border
                i4 = self.shape[1] - border

        data = self[max(i1, 0):min(i2, self.shape[0]), max(i3, 0):min(i4, self.shape[1])].copy()
        data[data.mask] = ndimage.filters.uniform_filter(data.data, size=pixelsize)[data.mask]
        smalldata = data[::pixelsize, ::pixelsize]
        try:
            # increase pixel size
            smalldata.pixel_size = [pz * pixelsize for pz in smalldata.pixel_size]
        except AttributeError:
            pass
        try:
            bc = self.beamcenter[:]
            bc[0] = (bc[0] - max(i1, 0)) / pixelsize
            bc[1] = (bc[1] - max(i3, 0)) / pixelsize
            smalldata.setBeamcenter(bc)
        except AttributeError:
            pass

        # set pixel coordinates
        smalldata.ImageWidth = [smalldata.shape[1]]
        smalldata.ImageLength = [smalldata.shape[0]]
        smalldata.XResolution[0] = data.XResolution[0] * float(pixelsize)
        smalldata.YResolution[0] = data.YResolution[0] * float(pixelsize)
        smalldata._setEXIF()
        return smalldata

    def showPolar(self, beamcenter=None, scaleR=1, offset=0):
        """
        Show image transformed to polar coordinates around beamcenter.

        Azimuth corresponds:
        center line to beamcenter upwards, upper quarter beamcenter to right
        upper/lower edge = beamcenter downwards, lower quarter beamcenter to left

        Parameters
        ----------
        beamcenter : [int,int]
            Beamcenter
        scaleR : float
            Scaling factor for radial component to zoom the beamcenter.
        offset : float
            Offset to remove beamcenter from polar image.

        Returns
        -------
            Handle to figure

        Examples
        --------
        Use radial averaged data to interpolate ::

         import jscatter as js
         import numpy as np
         calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         calibration.showPolar()

        """
        if beamcenter is not None:
            self.beamcenter = beamcenter

        # transform from polar coordinates to cartesian with bc shift and scaling of radial component to magnify
        def transform(rp, bc, shape, scale, offset):
            phi = rp[0] / shape[0] * 2 * np.pi - np.pi
            r = max(0, rp[1] + abs(offset)) / scale
            return r * np.cos(phi) + bc[0], r * np.sin(phi) + bc[1]

        newimage = np.zeros_like(self.data)
        ndimage.geometric_transform(self, mapping=transform, output=newimage,
                                    extra_keywords={'bc': self.beamcenter, 'shape': self.shape, 'scale': scaleR,
                                                    'offset': offset})

        f = mpl.contourImage(newimage, axis='pixel')
        f.axes[0].set_ylabel('azimuth ')
        f.axes[0].set_xlabel('radial / pixel')
        mpl.pyplot.show(block=False)

        return f

    def _polarCoordinates(self, beamcenter):
        X = (self.iX - beamcenter[0])
        Y = (self.iY - beamcenter[1])
        self._azimuth = np.arctan2(X, Y)
        self._radial = np.linalg.norm([X, Y], axis=0)

    def asdataArray(self, masked=0):
        """
        Return representation of sasImage as dataArray representing wavevectors (qx,qy) against intensity.

        Parameters
        ----------
        masked : float, None, string, default=0
            How to deal with masked values.
             - float : Set masked pixels to this value
             - None  : Remove from dataArray.
                       To recover the image the masked pixels need to be interpolated on a regular grid.
             - ‘linear’, ‘cubic’, ‘nearest’ : interpolate masked points by scipy.interpolate.griddata
                                              using specified order of interpolation on 2D image.
             - 'radial' Use the radial averaged data to interpolate.

        Returns
        -------
         dataArray with [qx,qy,I(qx,qy) ]
            - .qx, .qz : original qx values to recover the image

        Examples
        --------
        This demo will show the interpolation in the masked regions
        of an artificial intensity distribution. ::

         # manipulate data (not the mask)
         calibration.data[:150,30:60]=100
         calibration.data[:150,60:90]=300
         calibration.data[:150,90:]=600
         # mask a circle
         calibration.maskCircle([100,100], 60)
         cal=calibration.asdataArray('linear')
         cal.Y[cal.Y<=0.1]=1.1
         js.mpl.surface(cal.X, cal.Z, cal.Y)

         cal2=calibration.asdataArray(None)  # this is reduced in size due to the mask

        Use radial averaged data to interpolate ::

         import jscatter as js
         import numpy as np
         bsa = js.sas.sasImage(js.examples.datapath+'/BSA11mg.tiff')
         bsa.maskCircle(bsa.beamcenter,20)
         bsar=bsa.asdataArray('radial')
         js.mpl.surface(bsar.X, bsar.Z, bsar.Y)

        """
        qxz = self.getPixelQ()  # array of qx and qy
        qx = np.repeat(qxz[0][:, None], self.shape[1], axis=1)
        qz = np.repeat(qxz[1][None, :], self.shape[0], axis=0)
        # return flat array without masked data
        mask = ~self.mask.flatten()
        if isinstance(masked, (float, int)):
            out = dA(np.stack([qx.flatten(), qz.flatten(), self.data.flatten()]), XYeYeX=[0, 2, None, None, 1, None])
            out[2, ~mask] = masked
        elif isinstance(masked, basestring) and self.mask.sum() > 0:
            if masked not in ['linear', 'cubic', 'nearest','radial']:
                masked = 'nearest'
            qxf = qx.flatten()
            qzf = qz.flatten()
            dat = self.data.flatten()
            if masked[0] != 'r':
                # 2D interpolation for masked points
                f = griddata(np.stack([qxf[mask], qzf[mask]], axis=1), dat[mask], (qxf[~mask], qzf[~mask]), method=masked)
                dat[~mask] = f
                out = dA(np.stack([qxf, qzf, dat]), XYeYeX=[0, 2, None, None, 1, None])
            else:
                # interpolate from radial averaged image
                qr=la.norm([qxf,qzf],axis=0)
                # radial averaged data as dataarray with interp function
                radial=self.radialAverage()
                dat[~mask] = radial.interp(qr[~mask])
                out = dA(np.stack([qxf, qzf, dat]), XYeYeX=[0, 2, None, None, 1, None])
        else:
            out = dA(np.stack([qx.flatten()[mask], qz.flatten()[mask], self.flatten()[mask]]),
                     XYeYeX=[0, 2, None, None, 1, None])
        out.qx = qxz[0]
        out.qz = qxz[1]
        return out

    def interpolateMaskedRadial(self, radial=None):
        """
        Interpolate masked values from radial averaged image or function.

        This can be used to "extrapolate" over masked regions if e.g a background was measured
        at wrong distance.

        Parameters
        ----------
        radial : dataArray, function, default = None
            Determines how to determine masked values based on radial *q* values from beamcenter.
             - Function accepting array to calculate masked data.
             - dataArray for linear interpolating masked points.
             - None uses the radialAverage image.

        Returns
        -------
            sasImage including original parameters.

        Examples
        --------
        Use radial averaged data to interpolate ::

         import jscatter as js
         import numpy as np
         calibration = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         cal=calibration.interpolateMaskedRadial()
         # or
         # cal=calibration.interpolateMaskedRadial(calibration.radialAverage())
         cal.show()

        Generate image for different detector distance ::

         cal.setDetectorDistance(0.3)
         # mask whole image
         cal.mask=np.ma.masked
         # recover image with radial average from original
         cal2=cal.interpolateMaskedRadial(calibration.radialAverage())
         cal2.show()


        """
        qxz = self.getPixelQ()  # array of qx and qy
        qx = np.repeat(qxz[0][:, None], self.shape[1], axis=1)
        qz = np.repeat(qxz[1][None, :], self.shape[0], axis=0)
        # return flat array without masked data
        mask = self.mask.flatten()
        dat = self.data.flatten()
        qr = la.norm([qx.flatten(), qz.flatten()], axis=0)
        if formel._getFuncCode(radial):
            # is a function to call
            dat[mask] = radial(qr[mask])
        elif radial is None:
            # radial average in q units
            radial=self.radialAverage()
            dat[mask] = radial.interp(qr[mask])
        elif hasattr(radial,'_isdataArray'):
            dat[mask] = radial.interp(qr[mask])
        else:
            raise Exception('Unknown radial ')
        image = self.copy()
        image.data[self.mask] = dat.reshape(self.shape[0], self.shape[1])[self.mask]
        image.maskReset()
        return image

    def saveAsTIF(self, filename, fill=None, **params):
        """
        Save the sasImage as float32 tif without loosing information.

        Conversion from float64 to float32 is necessary.
        To save colored images use asImage.save() (see :py:func:`~sasImage.asImage`)

        Parameters
        ----------
        filename : string
            Filename to save to.
        fill : float, 'min' default None
            Fill value for masked values. By default this is -1.

            'min' uses the minimal value of the respective data type
             - np.iinfo(np.int32).min = -2147483648  for int32
             - np.finfo(np.float32).min = -3.4028235e+38 for float32
        params : kwargs
            Additional kwargs for PIL.Image.save if needed.

        Examples
        --------
        ::

         import jscatter as js
         cal = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         cal2=cal/2.
         cal2.saveAsTIF('mycal',fill=-100)
         mycal=js.sas.sasImage('mycal.tif',maskbelow=-200)
         mycal.show()

        """
        # create image
        _, file_extension = os.path.splitext(filename)
        if file_extension not in ['tif', 'tiff']:
            filename+='.tif'
        if fill is None:
            fill=-1
        if self.dtype == 'int32':
            if fill == 'min':
                fill = np.iinfo(np.int32).min
            image = PIL.Image.fromarray(self.filled(fill), mode='I')
        else:  # as float32
            if fill == 'min':
                fill = np.finfo(np.float32).min
            image = PIL.Image.fromarray(self.filled(fill).astype(np.float32), mode='F')
        # write image
        params.update({'tiffinfo': self._tags})
        image.save(fp=filename, **params)

    def asImage(self, scale='log', colormap='jet', inverse=False, linthresh=1.0, linscale=1.0):
        """
        Returns the sasImage as 8bit RGB image using PIL.

        See `PIL(Pillow) <https://pillow.readthedocs.io/en/latest/>`_ for more info about PIL images
        and image manipulation possibilities as e.g. in notes.
        Conversion to 8bit RGB looses floating point information but is for presenting and publication.

        Parameters
        ----------
        scale : 'log', 'symlog', default = 'norm'
            Scale for intensities.

            - 'norm' Linear scale.
            - 'log' Logarithmic scale
            - 'symlog' Symmetrical logarithmic scale is logarithmic in both the positive
              and negative directions from the origin.
              Use linthresh, linscale to adjust.
        colormap : string, None
            Colormap from matplotlib or None for grayscale.
            For standard colormap names look in js.mpl.showColors().
        inverse : bool
            Inverse colormap.
        linthresh : float, default = 1
            Only used for scale 'sym'.
            The range within which the plot is linear (-linthresh to linthresh).
        linscale : float, default = 1
            Only used for scale 'sym'.
            Its value is the number of decades to use for each half of the linear range.

        Returns
        -------
            PIL image

        Notes
        -----
        Pillow (fork of PIL)  allows image manipulation.
        As a prerequisite of Jscatter it is installed on your system and can be imported as ``import PIL`` ::

         image=mysasimage.asImage()
         image.show()                                             # show in system default viewer
         image.save('test.pdf', format=None, **params)            # save the image in different formats
         image.save('test.jpg',subsampling=0, quality=100)        # use these for best jpg quality
         image.save('test.png',transparency=(0,0,0))              # png image with black as transparent
         image.crop((10,10,200,200))                              # cut border

         import PIL.ImageOps as PIO
         nimage=PIO.equalize(image, mask=None)                    # Equalize the image histogram.
         nimage=PIO.autocontrast(image, cutoff=0, ignore=None)    # Automatic contrast
         nimage=PIO.expand(image, border=20, fill=(255,255,255))  # add border to image (here white)


        Examples
        --------
        ::

         import jscatter as js
         import PIL.ImageOps as PIO
         cal = js.sas.sasImage(js.examples.datapath+'/calibration.tiff')
         # create image for later usage
         image=cal.asImage(colormap='inferno',scale='log',inverse=1)
         # create image and just show it
         cal.asImage(colormap='inferno',scale='log').show()
         # expand image and show it or save it
         PIO.expand(image, border=20, fill=(255,255,255)).show()
         PIO.expand(image, border=20, fill=(255,255,255)).save('myimageas.pdf')

        """
        if colormap is not None:
            cmap = cm.get_cmap(colormap)
        else:
            cmap = cm.get_cmap('gray')

        if scale[:3] == 'log':
            norm=colors.LogNorm(clip=True)
        elif scale[:3] == 'sym':
            norm = colors.SymLogNorm(clip=True, linthresh=linthresh, linscale=linscale)
        else:  # default: scale == 'normalize':
            norm=colors.Normalize(clip=True)

        # initialize min,max values
        norm.autoscale(self)
        # do normalization
        data=norm(self)
        if inverse:
            data=1-data

        # conversion to colormap in range 0:255
        cdata = cmap(data, bytes=True)

        image = PIL.Image.fromarray(cdata[:, :, :-1], mode='RGB')

        return image


def readImages(filenames):
    """
    Read a list of images returning sasImage`s.

    Parameters
    ----------
    filenames : string
        Glob pattern to read

    Returns
    -------
        list of sasImage`s

    Notes
    -----
    To get a list of image descriptions::

     images=js.sas.readImages(path+'/latest*.tiff')
     [i.description for i in images]

    """
    try:
        filelist = glob.glob(filenames)
    except AttributeError:
        raise AttributeError('No filename pattern in ', filenames)
    else:
        data = []
        for ff in filelist:
            data.append(sasImage(ff))
    return data


def createImageDescriptions(images):
    """
    Create text file with image descriptions as list of content.

    Parameters
    ----------
    images : list of sasImages or glob pattern
        List of images

    Returns
    -------


    """
    if not isinstance(images, (list, set)):
        images = readImages(filenames)
    commonprefix = os.path.commonprefix([i.filename for i in images])
    description = [i.filename[len(os.path.dirname(commonprefix)) + 1:] + '   ' + i.description for i in images]
    description.sort()
    commonname = os.path.split(commonprefix)[-1]
    if commonname == '':
        commonname = '--'
    with open('ContentOf_' + commonname + '.txt', 'w') as f:
        f.writelines("%s\n" % l for l in ['Content of dir ' + os.path.dirname(commonprefix), ' '])
        f.writelines("%s\n" % l for l in description)


def createLogPNG(filenames, center=None, size=None, colormap='jet', equalize=False, contrast=None):
    """
    Create .png files from grayscale images with log scale conversion to values between [1,255].

    This generates images viewable in simple image viewers as overview.
    The new files are stored in the same folder as the original files.

    Parameters
    ----------
    filenames : string
        Filename with glob pattern as 'file*.tif'
    center : [int,int]
        Center of crop region.
    size : int
        Size of crop region.
         - If center is given a box with 2*size around center is used.
         - If center is None the border is cut by size.
    colormap : string, None
        Colormap from matplotlib or None for grayscale.
        For standard colormap names look in mpl.showColors().
    equalize : bool
        Equalize the images.
    contrast : None, float
        Autocontrast for the image.
        The value (0.1=10%) determines how much percent are cut from the intensity histogram before linear
        spread of intensities.

    """
    if colormap is not None:
        cmap = mpl.pyplot.get_cmap(colormap)
    else:
        cmap = None
    i1 = i3 = 0
    i2 = i4 = 100000
    if size is not None:
        # set box around center or from border
        if center is not None:
            i1 = center[1] - size
            i2 = center[1] + size
            i3 = center[0] - size
            i4 = center[0] + size
        else:
            i1 = size
            i2 = - size
            i3 = size
            i4 = - size
    try:
        filelist = glob.glob(filenames)
    except AttributeError:
        raise AttributeError('No filename pattern in ', filenames)
    else:
        for ff in filelist:
            image = PIL.Image.open(ff)
            # crop image array
            image2 = np.array(image)[max(i1, 0):min(i2, image.height), max(i3, 0):min(i4, image.width)]
            # log scale mapped to 0-255
            image2[image2 < 1] = 1
            image2 = np.log(image2)
            image2 = image2 / np.max(image2) * 255
            if cmap is None:
                newimage = PIL.Image.fromarray(image2.astype(np.uint8)).convert('L')
            else:
                # cmap needs uint to work properly
                image2 = cmap(image2.astype(np.uint8), bytes=True)
                newimage = PIL.Image.fromarray(image2[:, :, :-1], mode='RGB')
            if contrast is not None:
                newimage = PIL.ImageOps.autocontrast(newimage, contrast)
            if equalize:
                newimage = PIL.ImageOps.equalize(newimage)
            newimage.save(ff + '.png')
    return

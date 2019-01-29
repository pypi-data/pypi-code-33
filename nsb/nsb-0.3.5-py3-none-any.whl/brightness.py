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

import math
import numpy
import ephem
from . import nsbtools as tools
import matplotlib.pyplot as plt
from . import gaia as gaia
from operator import itemgetter

import numpy as np


class Brightness():
    def __init__(self, InputOptions, Conf, time1, time2, source, level=7, threshold=400, timeresolution=15):
        self.observer_sun = ephem.Observer()
        self.observer_sun.pressure = 0
        self.observer_sun.horizon = Conf.config['sun_below_horizon']
        self.observer_sun.lon, self.observer_sun.lat = Conf.config['Lon'], Conf.config['Lat']
        self.observer_sun.elevation = float(Conf.config['elevation'])

        self.observer_moon = ephem.Observer()
        self.observer_moon.pressure = 0
        self.observer_moon.horizon = Conf.config['moon_above_horizon']
        self.observer_moon.lon, self.observer_moon.lat = Conf.config['Lon'], Conf.config['Lat']
        self.observer_moon.elevation = float(Conf.config['elevation'])

        self.observer_source = ephem.Observer()
        self.observer_source.pressure = 0
        self.observer_source.horizon = Conf.config['source_above_horizon']
        self.observer_source.lon, self.observer_source.lat = Conf.config['Lon'], Conf.config['Lat']
        self.observer_source.elevation = float(Conf.config['elevation'])

        self.sun = ephem.Sun()
        self.moon = ephem.Moon()
        self.verbose = InputOptions.verbose
        self.offset = ephem.Date('0001/01/01 00:00:00')

        self.time_start = time1
        self.time_end = time2
        self.level = level
        self.threshold = threshold
        self.timeresolution = timeresolution

        if not source == None:
            pointing = source.name
            if source.name.lower().strip() == 'moon':
                self.source = self.moon
            else:
                self.source = ephem.FixedBody()
                self.source._ra, self.source._dec = source.ra, source.dec
                self.source.name = source.name
            self.source.compute(self.observer_source)
            self.alt = self.source.alt
            self.az = self.source.az
            print('* %s at \tzen %.2f\taz %.2f' % (self.source.name, math.degrees(np.pi/2 - self.alt), self.az))
        else:
            raise NotImplementedError("Please Track a source. Alt Az brightness not ready yet")


    def setHESSDate(self, date):
        self.observer_source.date = date
        self.observer_moon.date = date
        self.observer_sun.date = date

    def recomputeAll(self):
        self.source.compute(self.observer_source)
        self.moon.compute(self.observer_moon)
        self.moon_alpha = math.acos(self.moon.moon_phase * 2 - 1)
        self.sun.compute(self.observer_sun)

    def calculate(self):
        self.setHESSDate(self.time_start)
        self.recomputeAll()
        self.gaiamap = gaia.Gaia(level=self.level)
        self.timestamps = []
        self.bright = []
        self.moonphase = []
        self.moonalt = []
        self.sourcealt = []
        self.moonaz = []
        self.sourceaz = []
        self.sunalt = []
        self.sunaz = []
        self.separation = []


        t = self.time_start
        while t < self.time_end:
            self.setHESSDate(t)
            self.recomputeAll()
            self.timestamps.append(t - self.time_start)
            if self.source.alt > self.observer_source.horizon and self.sun.alt < self.observer_sun.horizon:
                if self.source.name.lower()=='moon':
                    ra, dec = self.observer_source.radec_of(self.source.az, self.source.alt)
                else:
                    ra, dec = self.source._ra, self.source._dec
                healpixid = self.gaiamap.healpix(math.degrees(ra), math.degrees(dec))
                self.bright.append(tools.B_moon(numpy.pi / 2. - self.source.alt,
                                           self.source.az, numpy.pi / 2. - self.moon.alt,
                                           self.moon.az, 0.479, self.moon_alpha) +
                              tools.B_sky(numpy.pi / 2. - self.source.alt,
                                          self.source.az,
                                          77.0,
                                          0.479) +
                              tools.MagnLb(self.gaiamap.getBrightness(healpixid)))


            else:
                self.bright.append(numpy.nan)

            self.moonphase.append(self.moon.moon_phase * 100)
            self.moonalt.append(math.degrees(self.moon.alt))
            self.moonaz.append(math.degrees(self.moon.az))
            self.sourcealt.append(math.degrees(self.source.alt))
            self.sourceaz.append(math.degrees(self.source.az))
            self.sunalt.append(math.degrees(self.sun.alt))
            self.sunaz.append(math.degrees(self.sun.az))
            if self.source.alt > self.observer_source.horizon and self.sun.alt < self.observer_sun.horizon and self.moon.alt > self.observer_moon.horizon:
                self.separation.append(math.degrees(tools.greatCircle(numpy.pi / 2. - self.source.alt,
                                                                 self.source.az,
                                                                 numpy.pi / 2. - self.moon.alt,
                                                                 self.moon.az)))
            else:
                self.separation.append(numpy.nan)

            t += 1.0 / (24 * (60/self.timeresolution))

        t = self.time_start - 1
        self.setHESSDate(self.time_start)
        self.recomputeAll()
        self.sunset = []
        self.sunrise = []
        while t < self.time_end:
            self.observer_sun.date = t
            sr = self.observer_sun.next_rising(self.sun)
            ss = self.observer_sun.next_setting(self.sun)

            t = ss + 0.25
            self.sunrise.append([float(sr - self.time_start), str(sr) + ' \tSunrise'])
            self.sunset.append([float(ss - self.time_start), str(ss) + ' \tSunset'])

        t = self.time_start - 1
        self.setHESSDate(self.time_start)
        self.recomputeAll()
        self.moonset = []
        self.moonrise = []
        while t < self.time_end:
            self.observer_moon.date = t
            mr = self.observer_moon.next_rising(self.moon)
            ms = self.observer_moon.next_setting(self.moon)
            t = ms + 0.25
            self.moonrise.append([float(mr - self.time_start), str(mr) + ' \tMoonrise'])
            self.moonset.append([float(ms - self.time_start), str(ms) + ' \tMoonset'])        
        
        t = self.time_start
        self.setHESSDate(self.time_start)
        self.recomputeAll()
        self.sourceset = []
        self.sourcerise = []
        while t < self.time_end:
            self.observer_source.date = t
            sor = self.observer_source.next_rising(self.source)
            sos = self.observer_source.next_setting(self.source)
            t = sos + 0.25
            self.sourceset.append([float(sos - self.time_start), str(sos) + ' \tSet of ' + self.source.name])
            self.sourcerise.append([float(sor - self.time_start), str(sor) + ' \tRise of ' + self.source.name])        

    def calculateOnce(self):
        self.setHESSDate(self.time_start)
        self.recomputeAll()
        self.gaiamap = gaia.Gaia(level=self.level)

        t = self.time_start

        self.setHESSDate(t)
        self.recomputeAll()
        if self.source.alt > self.observer_source.horizon and self.sun.alt < self.observer_sun.horizon:
            if self.source.name.lower()=='moon':
                ra, dec = self.observer_source.radec_of(self.source.az, self.source.alt)
            else:
                ra, dec = self.source._ra, self.source._dec
            healpixid = self.gaiamap.healpix(math.degrees(ra), math.degrees(dec))
            b = (tools.B_moon(numpy.pi / 2. - self.source.alt,
                                       self.source.az, numpy.pi / 2. - self.moon.alt,
                                       self.moon.az, 0.479, self.moon_alpha) +
                          tools.B_sky(numpy.pi / 2. - self.source.alt,
                                      self.source.az,
                                      77.0,
                                      0.479) +
                          tools.MagnLb(self.gaiamap.getBrightness(healpixid)))
            print("Sky-Brightness at source Position: %.2f nLb" %b)
        else:
            print("Source not up yet, or Sun still up")

    def plotObsTime(self):

        plt.figure()
        separation = np.nan_to_num(self.separation)
        bright = np.nan_to_num(self.bright)
        bright = bright[separation > 0]

        # keeps number of steps between 11 and 101
        steps = np.min([101, np.max([11, self.threshold])])
        self.brightness_range = np.linspace(0, self.threshold, steps)

        hours = []
        if self.verbose: print("total Observation Time gain of source %s during moontime\n max nsb\tgain total hours\t(hours per year)" % (self.source.name))
        for limit in self.brightness_range:
            h = np.sum(bright < limit) / (60/self.timeresolution)
            hours.append(h)
            if self.verbose: print("%.2f nLb,\t(%.2f hours),\t(%.2f hours/year)" % (limit, h , 365 * h / (self.time_end - self.time_start)))

        plt.plot(self.brightness_range, 365 * np.array(hours) / (self.time_end - self.time_start), label=self.source.name)
        plt.legend()
        ax = plt.gca()
        plt.title("Observation Time Gain with Moonlight")
        ax.set_xlabel('max allowed Brightness [nLb]')
        ax.set_ylabel('Moonlight Observation Time [h/year]')
        plt.show()


    def plotTimespan(self):
        # verbose timing output
        if self.verbose:
            all_times = self.sunset + self.sunrise + self.sourceset + self.sourcerise + self.moonset + self.moonrise
            all_times = sorted(all_times, key=itemgetter(0))
            sun_down = False
            for i in range(len(all_times)):
                if "Sunset" in all_times[i][1]:
                    sun_down = True
                if sun_down:
                    if i > 0 and not ("Sunset" in all_times[i][1]):
                        print("\t\t\t%.2f hours" % ((all_times[i][0]  - all_times[i-1][0])*24))
                    print(all_times[i][1])
                if "Sunrise" in all_times[i][1]:
                    sun_down = False
                    print()

        plt.rcParams['figure.figsize'] = 16, 12
        # fig, (sub1, sub2, sub3) = plt.subplots(3, 1, sharex=True)
        fig, (sub1, sub2) = plt.subplots(2, 1, sharex=True)
        plt.subplots_adjust(bottom=0.5)

        # source alt colorcoded
        co = []
        for value in self.sourcealt:
            co.append(numpy.interp(value, [0.0, 90.0], [0.0, 1.0]))


        if len(self.timestamps)<=50:
            labels = ['      %s' % ephem.Date(t + self.time_start) for t in self.timestamps]
            plt.xticks(self.timestamps, labels, rotation=90)
        elif len(self.timestamps)> 50 and (self.time_end - self.time_start) < 15:
            ticks = []
            labels = []
            t = 0
            while t < (self.time_end - self.time_start):
                t += 0.25
                ticks.append(t)
                labels.append("      " + str(ephem.Date(t + self.time_start)))
            plt.xticks(ticks, labels, rotation=90)

        elif (self.time_end - self.time_start) < 50:
            ticks = []
            labels = []
            t = 0
            while t < (self.time_end - self.time_start):
                t += 1
                ticks.append(t)
                labels.append("      " + str(ephem.Date(t + self.time_start)))
            plt.xticks(ticks, labels, rotation=90)

        else:
            plt.xlabel('Days since %s' % self.time_start)

        sub1.minorticks_on()
        sub2.minorticks_on()

        sub1.set_title('estimated sky-brightness for position of source "%s"' % self.source.name)
        # sub1.scatter(self.timestamps, self.bright, s=1, c=co, label='brightness')
        sub1.scatter(self.timestamps, self.bright, s=1, label='brightness')
        sub1.set_ylim(bottom=0)
        sub1.set_xlim(left=0, right=self.time_end - self.time_start)
        sub1.axhline(y=400, linewidth=0.2, color='black')
        sub1.set_ylabel('Brightnes [nLb]')

        sub2.plot(self.timestamps, self.moonphase, label='moon phase')
        sub2.plot(self.timestamps, self.separation, label='self.separation')
        sub2.plot(self.timestamps, self.moonalt, label='moon alt')
        sub2.plot(self.timestamps, self.sourcealt, label='source alt')
        sub2.set_xlim(left=0, right=self.time_end - self.time_start)
        sub2.axhspan(80, 100, facecolor='grey', alpha=0.2)
        sub2.axhline(y=0, linewidth=0.2, color='black')
        sub2.set_ylabel('Alt, Sep [deg]\nPhase [%]')

        # put the orange and grey bands for dayligt and moonlight
        for i in range(0, len(self.sunrise)):
            sub1.axvspan(self.sunrise[i][0], self.sunset[i][0], facecolor='orange', alpha=0.1)
            sub2.axvspan(self.sunrise[i][0], self.sunset[i][0], facecolor='orange', alpha=0.1)

        for i in range(0, len(self.moonrise)):
            sub1.axvspan(self.moonrise[i][0], self.moonset[i][0], facecolor='grey', alpha=0.1)
            sub2.axvspan(self.moonrise[i][0], self.moonset[i][0], facecolor='grey', alpha=0.1)

        sub1.legend(loc='upper right')
        sub2.legend(loc='upper right')

        # Pad margins so that markers don't get clipped by the axes
        #plt.margins(0.2)
        fig.tight_layout()
        plt.tight_layout()
        plt.draw()
        fname = "%s_%s_-_%s.pdf" % (self.source.name, self.time_start, self.time_end)
        fname = fname.replace(" ", "_").replace("/", "-")

        # plt.savefig("star_baselines/" + fname, papertype="a4", dpi=300)

        plt.show()


#

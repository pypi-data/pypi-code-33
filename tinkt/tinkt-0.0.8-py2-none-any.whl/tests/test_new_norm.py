#!/usr/bin/env python

from konfluence import Konfluence
from pylab import *
from tinkt.klasses import *

kfl = Konfluence()
kfl.register('colormap', ColorMap, generator='generate')
kfl.register('colornorm', ColorNorm, generator='generate')
kfl.register('colorspec', ColorSpec)

spec = kfl.get('colorspec/test3')

print spec.cmap, spec.norm

data = np.random.rand(12, 20) * 2500

spec.cmap.set_under('none')
plt.pcolormesh(data, cmap=spec.cmap, norm=spec.norm)
plt.colorbar()

plt.show()
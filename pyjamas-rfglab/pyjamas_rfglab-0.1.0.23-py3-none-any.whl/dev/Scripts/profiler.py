import cProfile
import pstats

from skimage import io

import rimage.rimcore as pyim
from dev import rimage_c as cim

anIm = io.imread('../python/test2.tif')
im = anIm[1, 0:10, 0:10]

a = pyim.rimage(im)
b = cim.CImage(im)

cProfile.runctx("b.makeGraph(im)", globals(), locals(), "Profile.prof")

s = pstats.Stats("Profile.prof")
s.strip_dirs().sort_stats("time").print_stats()
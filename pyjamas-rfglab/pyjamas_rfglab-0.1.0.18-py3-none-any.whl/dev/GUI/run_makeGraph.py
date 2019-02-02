import dev
import numpy

theimage = numpy.asarray([[3, 4, 6], [1, 2, 3], [2, 3, 5]])
a, b = dev.rimage_c.rimcore.RImage.makeGraph(theimage)
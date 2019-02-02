from pyjamas_package.pyjamas import PyJAMAS

a = PyJAMAS()
a._cbLoadTS.cbLoadTimeSeries('/Users/rodrigo/Documents/WORK/NUCLEAR_SEGMENTATION/0703_Stitched_488_-1.tif')
a._cbLoadClassifier.cbLoadClassifier('/Users/rodrigo/Documents/WORK/NUCLEAR_SEGMENTATION/0703_Stitched_488_-1_subimages_41_46/training/svm.cfr')
a._cbApplyClassifier.cbApplyClassifier(1, 1)
a._cbNonMaxSuppression.cbNonMaxSuppression()

# ----------------------------------------------------------------------------------------------------------------------

from pyjamas_package.pyjamas import PyJAMAS
import numpy

a = PyJAMAS()
a._cbLoadTS.cbLoadTimeSeries('/Users/rodrigo/Documents/WORK/NUCLEAR_SEGMENTATION/0703_Stitched_488_-1_subimages_41_46/test/tp2.tif')
a._cbLoadClassifier.cbLoadClassifier('/Users/rodrigo/Documents/WORK/NUCLEAR_SEGMENTATION/0703_Stitched_488_-1_subimages_41_46/training/svm.cfr')
a._cbApplyClassifier.apply_classifier(numpy.asarray([0], dtype=int))

# ----------------------------------------------------------------------------------------------------------------------

from pyjamas_package.pyjamas import PyJAMAS

a = PyJAMAS()
a._cbLoadTS.cbLoadTimeSeries('/Users/rodrigo/Documents/WORK/NUCLEAR_SEGMENTATION/0703_Stitched_488_-1.tif')
a._cbLoadClassifier.cbLoadClassifier('/Users/rodrigo/Documents/WORK/NUCLEAR_SEGMENTATION/0703_Stitched_488_-1_subimages_41_46/training/svm.cfr')
a._cbApplyClassifier.cbApplyClassifier()
a._cbNonMaxSuppression.cbNonMaxSuppression()
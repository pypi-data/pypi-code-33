"""
CEST Quantiphyse plugin

Author: Martin Craig <martin.craig@eng.ox.ac.uk>
Copyright (c) 2016-2017 University of Oxford, Martin Craig
"""
import os

from .widget import CESTWidget

QP_MANIFEST = {
    "widgets" : [CESTWidget],
    "fabber_dirs" : [os.path.dirname(__file__)],
}

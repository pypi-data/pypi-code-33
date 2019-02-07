"""
CEST Quantiphyse plugin

Author: Martin Craig <martin.craig@eng.ox.ac.uk>
Copyright (c) 2016-2017 University of Oxford, Martin Craig
"""
from quantiphyse.utils import get_local_shlib

from .widget import CESTWidget

QP_MANIFEST = {
    "widgets" : [CESTWidget],
    "fabber-libs" : [get_local_shlib("fabber_models_cest", __file__)]
}

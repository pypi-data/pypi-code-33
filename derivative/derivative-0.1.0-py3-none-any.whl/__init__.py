from .loc import *
from .glob import *


methods = {
    "finitediff": finitediff,
    "holoborodko": holoborodko,
    "fft_deriv": fft_deriv,
    "cubic_spline": cubic_spline_deriv,
    "tvregdiff": tvregdiff,
}


def derivative(x, y, kind="finitediff", **kwargs):
    method = methods.get(kind)
    if len(y.shape) > 1:
        return np.apply_along_axis(method, x, y, **kwargs)
    else:
        return method(x, y, **kwargs)

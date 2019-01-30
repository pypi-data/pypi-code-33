import numpy as np
import pandas as pd

class orthotope_error_c (Exception):
    pass

# axis_vars: pd.Series <axis_var, index>

def axis_vars_c (axis_vars, axis_name):
    if type (axis_vars) == list:
        return pd.Series (
            range (len (axis_vars)),
            index = axis_vars,
            name = axis_name)
    elif type (axis_vars) == dict:
        return pd.Series (
            axis_vars,
            name = axis_name)
    elif type (axis_vars) == pd.Series:
        return axis_vars
    else:
        raise orthotope_error_c

# axes: pd.Series <axis_name, pd.Series <axis_var, index>>

def axes_c (axes):
    axes = pd.Series (axes)
    values = []
    for axis_name, axis_vars in axes.iteritems ():
        values.append (axis_vars_c (axis_vars, axis_name))

    return pd.Series (
        values,
        index = axes.index)

def shape_of_axes (axes):
    axes = axes_c (axes)
    return tuple (map (len, axes.values))

def full (axes, v):
    # axes_c, value -> orthotope_c
    axes = axes_c (axes)
    shape = shape_of_axes (axes)
    tensor = np.full (shape, v)
    return orthotope_c (axes, tensor)

def zeros (axes):
    # axes_c -> orthotope_c
    axes = axes_c (axes)
    shape = shape_of_axes (axes)
    tensor = np.zeros (shape)
    return orthotope_c (axes, tensor)

class orthotope_c:
    def __init__ (self, axes, tensor):
        self.axes = axes_c (axes)
        self.shape = shape_of_axes (self.axes)
        if self.shape != tensor.shape:
            print ("- orthotope_c fail")
            print ("  self.shape != tensor.shape")
            print ("  self.shape = {}".format(self.shape))
            print ("  tensor.shape = {}".format(tensor.shape))
            raise orthotope_error_c
        if type (tensor) != np.ndarray:
            print ("- orthotope_c fail")
            print ("  type(tensor) = {}".format(type(tensor)))
            raise orthotope_error_c
        self._tensor = tensor

    def tensor (self):
        return self._tensor

    # idx: pd.Series <axis_name, axis_var>

    def idx_c (self, idx):
        return pd.Series (idx, index = self.axes.index)

    # idx_item: (axis_name, axis_var)

    def idx_item_to_index (self, idx_item):
        axis_name, axis_var = idx_item
        if pd.isna (axis_var):
            return slice (None)
        else:
            return self.axes [axis_name] [axis_var]

    def idx_to_index (self, idx):
        return tuple (list (map (
            self.idx_item_to_index,
            idx.items ())))

    def proj_to_tensor (self, idx):
        # orthotope_c, idx_c -> np.tensor
        idx = self.idx_c (idx)
        index = self.idx_to_index (idx)
        return self._tensor [index]

    def proj (self, idx):
        # orthotope_c, idx_c -> orthotope_c
        idx = self.idx_c (idx)
        axes = self.axes [ idx.isna () ]
        tensor = self.proj_to_tensor (idx)
        return orthotope_c (axes, tensor)

    def let (self, idx, tensor):
        idx = self.idx_c (idx)
        index = self.idx_to_index (idx)
        self._tensor [index] = tensor

    def to_data_frame (self):
        # orthotope_c -> pd.DataFrame
        assert self.axes.size == 2
        index = pd.Index (
            self.axes [0] .sort_values () .index,
            name = self.axes [0] .name)
        columns = pd.Index (
            self.axes [1] .sort_values () .index)
        return pd.DataFrame (
            self._tensor,
            index = index,
            columns = columns)

    def to_series (self):
        # orthotope_c -> pd.Series
        assert self.axes.size == 1
        index = pd.Index (
            self.axes [0] .sort_values () .index,
            name = self.axes [0] .name)
        return pd.Series (
            self._tensor,
            index = index)

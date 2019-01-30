import numpy as np
import pandas as pd

def list_intersect (x, y):
    return list (filter (lambda e: e in y, x))

def list_difference (x, y):
    return list (filter (lambda e: e not in y, x))

class data_cube_c:
    def __init__ (self, df, attr_name_list, indi_name_list):
        column_name_list = list (df.columns)
        attr_name_list = list_intersect (attr_name_list, column_name_list)
        indi_name_list = list_intersect (indi_name_list, column_name_list)
        name_list = attr_name_list + indi_name_list
        df = pd.DataFrame (df, columns = name_list)
        self.df = df
        self.attr_name_list = attr_name_list
        self.indi_name_list = indi_name_list

    def __repr__ (self):
        s = "\n"
        s += self.df.__repr__ ()
        s += "\n"
        s += "attr_name_list = {}" .format (self.attr_name_list)
        s += "\n"
        s += "indi_name_list = {}" .format (self.indi_name_list)
        return s

    def proj (self, itemdict):
        df = self.df
        for k, v in itemdict.items ():
            df = df [ df [k] .isin ([v]) ]
        return data_cube_c (
            df,
            self.attr_name_list,
            self.indi_name_list)

    def proj_drop (self, itemdict):
        cube = self.proj (itemdict)
        return data_cube_c (
            cube.df.drop (columns = itemdict.keys ()),
            self.attr_name_list,
            self.indi_name_list)

    def retract (self, attr_name_list):
        df = self.df
        rest_name_list = list_difference (
            self.attr_name_list, attr_name_list)
        df = df.drop (columns = attr_name_list)
        if hasattr (df.index, "name"):
            index_name = df.index.name
        else:
            index_name = None

        df.index = df.index.set_names (["_index"])
        df = df.reset_index ()
        df = df.groupby (
            ["_index"] + rest_name_list,
            as_index = False,
        ) .sum ()
        df = df.set_index ("_index")
        df.index.name = index_name
        return data_cube_c (
            df,
            self.attr_name_list,
            self.indi_name_list)

    def retract_all (self):
        return self.retract (self.attr_name_list)

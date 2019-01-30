"""
This module handles the data creation and handling of dlc_gui.

It creates the main pandas DataFrame, QColor color palette, and `images_paths_dict`.
"""


import os
import glob

import numpy as np
import pandas as pd
from tables.exceptions import NoSuchNodeError

import dlc_gui.util


class DataModel:
    """
    Create useful data structures such as the main pandas DataFrame used by DeepLabCut,
    the images_paths_dict which keeps allows translation between abs and rel paths,
    and the color palette.
    """

    def __init__(self, config_path):
        # Initialize without a given directory of frames or a h5 file
        # Define attributes as empty or None, because the rest of the code
        # expects their existence
        self.config_path = config_path
        self.config_dict = dlc_gui.util.read_config_file(self.config_path)

        self.scorer = self.config_dict["scorer"]
        self.bodyparts = self.config_dict["bodyparts"]
        self.project_path = os.path.abspath(self.config_dict["project_path"])

        try:
            f = open(os.path.join(self.project_path, "config.yaml"), "r")
            f.close()
        except FileNotFoundError as e:
            raise FileNotFoundError(
                "The 'project_path' variable in config.yaml is invalid."
            ) from e
        self.colors, self.colors_opposite, self.colors_opaque = self.color_palette(
            len(self.bodyparts)
        )

        # TODO find replacement for pd.concat to avoid defining as None
        self.data_frame = None
        self.images_paths_dict = {}

    def init_from_dir(self, dir):
        # Defines self.images_paths_dict and self.data_frame based on a dir
        self.images_paths = sorted(glob.glob(os.path.join(dir, "*.png")))

        if self.images_paths:
            # The commented out code causes an error with pytables.
            # It is currently unknown why.
            # init_nan = np.empty((len(self.images_paths), 2)).fill(np.nan)
            init_nan = np.empty((len(self.images_paths), 2))
            init_nan[:] = np.nan

            self.images_relpaths = [
                os.path.relpath(image_path, self.project_path)
                for image_path in self.images_paths
            ]

            self.images_paths_dict = dict(zip(self.images_relpaths, self.images_paths))

            for bodypart in self.bodyparts:
                index = pd.MultiIndex.from_product(
                    [[self.scorer], [bodypart], ["x", "y"]],
                    names=["scorer", "bodyparts", "coords"],
                )
                frame = pd.DataFrame(
                    init_nan, columns=index, index=self.images_relpaths
                )
                self.data_frame = pd.concat([self.data_frame, frame], axis=1)

    def init_from_file(self, file):
        # Defines self.images_paths_dict and self.data_frame based on a h5 file
        # Due to the inconsistencies between ``to_csv``, ``from_csv``,
        # ``read_csv``, etc., ONLY '.h5' files will be accepted.
        # https://github.com/pandas-dev/pandas/issues/13262
        if file:
            if "h5" in file:
                self.NoSuchNodeError = NoSuchNodeError
                try:
                    self.data_frame = pd.read_hdf(file, "df_with_missing")
                except KeyError as e:
                    raise KeyError(
                        "The group identifier 'df_with_missing' was not found in the file."
                    ) from e
                except self.NoSuchNodeError as e:
                    raise self.NoSuchNodeError(
                        "This hdf file is missing a table."
                    ) from e
            elif "pkl" in file:
                self.data_frame = pd.read_pickle(file)
            try:
                self.images_relpaths = sorted(self.data_frame.index.tolist())
            except AttributeError as e:
                raise AttributeError(
                    "The list of frames could not be read from the .h5 file."
                ) from e
            self.images_paths = [
                os.path.join(self.project_path, i) for i in self.images_relpaths
            ]

            # TODO avoid copy pasted code
            self.images_paths_dict = dict(zip(self.images_relpaths, self.images_paths))

    def color_palette(self, number):
        # Create a list of QColors and their opposites equal in length to the
        # number of bodyparts
        # TODO set alpha from config
        hues = np.linspace(0, 1, number, endpoint=False)

        colors = [(h, 1, 1, 0.5) for h in hues]
        colors_opposite = [(abs(0.5 - h), 1, 1, 0.5) for h in hues]
        colors_opaque = [(h, 1, 1, 1) for h in hues]

        return colors, colors_opposite, colors_opaque

    def add_coords_to_dataframe(self, frame, bodypart, coords):
        if all(coord is None for coord in coords):
            coords = (np.nan, np.nan)
        try:
            self.data_frame.loc[frame, self.scorer][bodypart, "x"] = coords[0]
            self.data_frame.loc[frame, self.scorer][bodypart, "y"] = coords[1]
        except KeyError as e:
            raise KeyError(
                "The scorer of the config.yaml does not match this .h5 file."
            ) from e

    def get_coords_from_dataframe(self, frame, bodypart):
        x = self.data_frame.loc[frame, self.scorer][bodypart, "x"]
        y = self.data_frame.loc[frame, self.scorer][bodypart, "y"]
        if np.isnan(x) and np.isnan(y):
            x, y = None, None

        return (x, y)

    def save_as_pkl(self, path):
        if path:
            pd.to_pickle(self.data_frame, path)

    def save(self, path):
        if path:
            self.data_frame.to_hdf(path, "df_with_missing", format="table", mode="w")

"""
This module handles the data creation and handling of dlc_gui.

It creates the main pandas DataFrame, color palette, and `frames_dict`.
`frames_dict` is a dictionary of frame_name (str): frame_path (path object) pairs.
"""

# TODO make sure each exception encloses paths with quotes

from pathlib import Path
from typing import List, Tuple, Union

import numpy as np
import pandas as pd

import dlc_gui.util


class DataModel:
    """
    Create useful data structures such as the main pandas DataFrame used by DeepLabCut,
    the frames_dict which keeps allows translation between abs and rel paths,
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

        # Make sure the project path is valid and exists
        try:
            self.project_path = Path(self.config_dict["project_path"]).resolve()
            if not self.project_path.is_dir():
                raise FileNotFoundError(
                    "'project_path' ({0}) in config.yaml does not exist.".format(
                        self.config_dict["project_path"]
                    )
                )
        except TypeError as e:
            raise TypeError(
                "'project_path' in config.yaml has an invalid type of {0}".format(
                    type(self.config_dict["project_path"])
                )
            ) from e

        self.colors, self.colors_opposite, self.colors_opaque = self.color_palette(
            len(self.bodyparts)
        )

        # Define variables to be used in gui.py for QFileDialog default dirs
        self.labeled_data_path = self.project_path / "labeled-data"
        self.save_path_hdf = self.labeled_data_path / "CollectedData_{}.h5".format(
            self.scorer
        )
        self.save_path_pkl = self.labeled_data_path / "CollectedData_{}.pkl".format(
            self.scorer
        )

        # TODO find replacement for pd.concat to avoid defining as None
        self.data_frame = None
        self.frames_dict = {}

    def init_from_dir(self, dir: Union[str, Path]) -> None:
        # Defines self.frames_dict and self.data_frame based on a dir

        dir = Path(dir)

        if self.project_path not in dir.parents:
            raise ValueError(
                "'{0}' is not within the project path ('{1}').".format(
                    dir, self.project_path
                )
            )

        try:
            self.frames_paths = sorted(Path(dir).glob("*.png"))

            # The commented out code causes an error with pytables.
            # It is currently unknown why.
            # init_nan = np.empty((len(self.images_paths), 2)).fill(np.nan)
            init_nan = np.empty((len(self.frames_paths), 2))
            init_nan[:] = np.nan

            self.frames_names = [
                str(Path(frame_path).relative_to(self.project_path))
                for frame_path in self.frames_paths
            ]

            self.frames_dict = dict(zip(self.frames_names, self.frames_paths))

            for bodypart in self.bodyparts:
                index = pd.MultiIndex.from_product(
                    [[self.scorer], [bodypart], ["x", "y"]],
                    names=["scorer", "bodyparts", "coords"],
                )
                frame = pd.DataFrame(init_nan, columns=index, index=self.frames_names)
                self.data_frame = pd.concat([self.data_frame, frame], axis=1)
        except (TypeError, ValueError):
            pass

    def init_from_file(self, file: Union[str, Path]) -> None:
        # Defines self.frames_dict and self.data_frame based on a h5 file
        # Due to the inconsistencies between ``to_csv``, ``from_csv``,
        # ``read_csv``, etc., ONLY '.h5' files will be accepted.
        # https://github.com/pandas-dev/pandas/issues/13262
        # TODO Proper extension checking

        file = Path(file)

        if file.is_file():
            if file.suffix in (".hdf", ".h5"):
                try:
                    self.data_frame = pd.read_hdf(file, "df_with_missing")
                except KeyError as e:
                    raise KeyError(
                        "The group 'df_with_missing' was not found in the .h5 file."
                    ) from e

            elif file.suffix in (".pkl", ".pickle"):
                self.data_frame = pd.read_pickle(file)

            try:
                self.frames_names = sorted(self.data_frame.index.tolist())
            except AttributeError as e:
                raise AttributeError(
                    "Could not find the DataFrame index from the file ('{0}').".format(
                        file
                    )
                ) from e

            self.frames_paths = [Path(self.project_path, _) for _ in self.frames_names]

            # TODO avoid copy pasted code
            self.frames_dict = dict(zip(self.frames_names, self.frames_paths))

    def color_palette(self, number: int) -> Tuple[List, List, List]:
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

        if np.isnan(x):
            x = None
        if np.isnan(y):
            y = None

        return (x, y)

    def save_as_pkl(self, path):
        if path:
            pd.to_pickle(self.data_frame, path)

    def save_as_hdf(self, path):
        if path:
            self.data_frame.to_hdf(path, "df_with_missing", format="table", mode="w")

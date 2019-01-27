"""
This module is the main file that handles everything.

This module attempts to keep a separation between the data/logic and GUI design.
"""

# TODO fix bug of unresponsive shortcuts of menubar

import argparse
import glob
import os
import sys
import webbrowser

from PySide2.QtCore import QEvent, QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QKeySequence, QPen, QPixmap
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QFileDialog,
    QGraphicsEllipseItem,
    QGraphicsScene,
    QGraphicsView,
    QGridLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QShortcut,
    QSlider,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

import numpy as np

import pandas as pd

import yaml


class DataModel:
    """
    Create useful data structures such as the main pandas DataFrame used by DeepLabCut,
    the images_paths_dict which keeps allows translation between abs and rel paths,
    and the color palette.
    """

    def __init__(self, config):
        # Initialize without a given directory of frames or a h5 file
        # Define attributes as empty or None, because the rest of the code
        # expects their existence
        self.config = config
        with open(config, "r") as f:
            self.config_dict = yaml.load(f)

        self.scorer = self.config_dict["scorer"]
        self.bodyparts = self.config_dict["bodyparts"]
        self.project_path = self.config_dict["project_path"]

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
            init_nan = np.empty((len(self.images_paths), 2)).fill(np.nan)

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
            self.data_frame = pd.read_hdf(file, "df_with_missing")

            # assumes structure, may not be reliable
            self.images_relpaths = sorted(self.data_frame.index.tolist()[2:])
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

        colors = [QColor.fromHsvF(h, 1, 1, 0.5) for h in hues]
        colors_opposite = [QColor.fromHsvF(abs(0.5 - h), 1, 1, 0.5) for h in hues]
        colors_opaque = [QColor.fromHsvF(h, 1, 1, 1) for h in hues]

        return colors, colors_opposite, colors_opaque

    def add_coords_to_dataframe(self, frame, bodypart, coords):
        self.data_frame.loc[frame, self.scorer][bodypart, "x"] = coords[0]
        self.data_frame.loc[frame, self.scorer][bodypart, "y"] = coords[1]

    def get_coords_from_dataframe(self, frame, bodypart):
        x = self.data_frame.loc[frame, self.scorer][bodypart, "x"]
        y = self.data_frame.loc[frame, self.scorer][bodypart, "y"]

        return tuple([x, y])

    def save(self, path):
        if path:
            self.data_frame.to_hdf(path, "df_with_missing", format="table", mode="w")


class GraphicsScene(QGraphicsScene):
    def __init__(self, parent):
        super(GraphicsScene, self).__init__(parent)

    def load_image(self, image):
        # Load frame png into scene
        self.frame_image = QPixmap()
        self.frame_image.load(image)
        self.addPixmap(self.frame_image)


class GraphicsView(QGraphicsView):
    def __init__(self, parent):
        super(GraphicsView, self).__init__(parent)

        self.scene = GraphicsScene(self)

        self.setScene(self.scene)
        self.fitInView(self.scene.sceneRect(), aspectRadioMode=Qt.KeepAspectRatio)

        self.viewport().setCursor(Qt.CrossCursor)

        # keep track of the current scale value to prevent zooming too far out
        self.scale_current = 1.0

    def wheelEvent(self, event):
        # Implement zooming with ctrl + mousewheel,
        # horizontal scrolling with shift + mousewheel,
        # and vertical scrolling with mousewheel

        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.setResizeAnchor(QGraphicsView.NoAnchor)

        # check which modifier key is held while wheel is scrolled
        modifiers = QApplication.keyboardModifiers()

        if modifiers == Qt.ControlModifier:

            scale_factor = 1.25

            old_pos = self.mapToScene(event.pos())

            scale_min = 0.3

            if event.delta() > 0:
                self.scale(scale_factor, scale_factor)
                self.scale_current *= scale_factor
            elif self.scale_current > scale_min:
                self.scale(1 / scale_factor, 1 / scale_factor)
                self.scale_current /= scale_factor

            new_pos = self.mapToScene(event.pos())

            delta = new_pos - old_pos
            self.translate(delta.x(), delta.y())

        elif modifiers == Qt.ShiftModifier:
            self.translate(event.delta(), 0)

        else:
            self.translate(0, event.delta())


class Widget(QWidget):
    """
    Create the main user interface and controls, connected to DataModel
    """

    def __init__(self, parent, config):
        super(Widget, self).__init__(parent)

        # Read config
        self.config = config
        with open(self.config, "r") as f:
            self.config_dict = yaml.load(f)
        self.project_path = self.config_dict["project_path"]

        # Create the main widgets
        self.graphics_view = GraphicsView(self)
        self.bodyparts_view = QListWidget()
        self.dot_size_slider = QSlider(Qt.Horizontal)
        self.dot_size_label = QLabel(parent=self.dot_size_slider)
        self.frames_view = QListWidget()

        # Set up the dot_size_slider
        dot_size_from_config = self.config_dict["dotsize"]
        self.dot_size_slider.setMinimum(1)
        self.dot_size_slider.setMaximum(100)
        self.dot_size_slider.setValue(dot_size_from_config)
        self.dot_size_slider.setTickPosition(QSlider.TicksBothSides)
        self.dot_size_slider.setTickInterval(10)
        self.dot_size_label.setText(
            "Label dot size: {} (from config.yaml)".format(dot_size_from_config)
        )
        self.dot_size_slider.sliderReleased.connect(
            lambda: self.dot_size_label.setText(
                "Label dot size: {}".format(self.dot_size_slider.value())
            )
        )

        self.dot_size_slider.sliderReleased.connect(lambda: self.update_scene())

        # Add a widget to add a layout containing the bodyparts and the slider
        labeling_widget = QWidget()
        labeling_layout = QVBoxLayout()
        labeling_layout.addWidget(self.bodyparts_view)
        labeling_layout.addWidget(self.dot_size_label)
        labeling_layout.addWidget(self.dot_size_slider)
        labeling_widget.setLayout(labeling_layout)

        # Set the main layout of Widget
        main_layout = QGridLayout()
        splitter = QSplitter()

        splitter.addWidget(self.frames_view)
        splitter.addWidget(self.graphics_view)
        splitter.addWidget(labeling_widget)

        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # Init widget properties from config and other data
        self.init_from_data_model_from_nothing()

        # Set up events
        self.frames_view.currentItemChanged.connect(lambda x: self.update_scene())

        self.graphics_view.scene.installEventFilter(self)

        shortcut_next_bodypart = QShortcut(QKeySequence("d"), self)
        shortcut_prev_bodypart = QShortcut(QKeySequence("a"), self)
        shortcut_next_frame = QShortcut(QKeySequence("s"), self)
        shortcut_prev_frame = QShortcut(QKeySequence("w"), self)
        # setattr is used as an assignment function, because lambdas cannot assign
        # prior to python 3.8
        shortcut_next_bodypart.activated.connect(
            lambda: setattr(self, "current_bodypart_row", self.current_bodypart_row + 1)
        )
        shortcut_prev_bodypart.activated.connect(
            lambda: setattr(self, "current_bodypart_row", self.current_bodypart_row - 1)
        )
        shortcut_next_frame.activated.connect(
            lambda: setattr(self, "current_frame_row", self.current_frame_row + 1)
        )
        shortcut_prev_frame.activated.connect(
            lambda: setattr(self, "current_frame_row", self.current_frame_row - 1)
        )

    def init_from_data_model_from_nothing(self):
        data_model = DataModel(self.config)
        self.init_from_data_model(data_model)

    def init_from_data_model_from_file(self):
        data_model = DataModel(self.config)
        data_model.init_from_file(
            QFileDialog.getOpenFileName(dir=self.project_path, filter="(*.hdf *.h5)")[0]
        )
        self.init_from_data_model(data_model)

    def init_from_data_model_from_dir(self):
        data_model = DataModel(self.config)
        dir = QFileDialog.getExistingDirectory(dir=self.project_path)
        data_model.init_from_dir(dir)
        if not data_model.images_paths_dict and dir:
            self.send_status("No images files (*.png) found in {}".format(dir), 5)
        self.init_from_data_model(data_model)

    def init_from_data_model(self, data_model):

        self.data_model = data_model

        self.bodyparts = self.data_model.bodyparts

        if self.data_model.images_paths_dict:
            self.images_paths_dict = self.data_model.images_paths_dict

            self.frames_view.clear()
            for frame in self.images_paths_dict.keys():
                self.frames_view.addItem(frame)

        self.bodyparts_view.clear()
        for bodypart in self.bodyparts:
            self.bodyparts_view.addItem(bodypart)

        # Set initial selections for both listwidgets
        frames_view_items = self.frames_view.findItems("*", Qt.MatchWildcard)
        if frames_view_items:
            self.frames_view.setCurrentItem(frames_view_items[0])
            self.graphics_view.scene.load_image(
                list(self.images_paths_dict.values())[0]
            )

        self.bodyparts_view_items = self.bodyparts_view.findItems("*", Qt.MatchWildcard)
        if self.bodyparts_view_items:
            self.bodyparts_view.setCurrentItem(self.bodyparts_view_items[0])
            for item, color in zip(
                self.bodyparts_view_items, self.data_model.colors_opaque
            ):
                pixmap = QPixmap(100, 100)
                pixmap.fill(color)
                item.setIcon(pixmap)

        self.update_scene()

    def eventFilter(self, obj, event):
        if (
            obj is self.graphics_view.scene
            and event.type() == QEvent.Type.GraphicsSceneMousePress
        ):

            scene_pos = event.scenePos()
            coords = tuple([scene_pos.x(), scene_pos.y()])

            frame = self.current_frame_text
            bodypart = self.current_bodypart_text

            if frame and bodypart:
                if event.buttons() == Qt.LeftButton:
                    self.data_model.add_coords_to_dataframe(frame, bodypart, coords)
                elif event.buttons() == Qt.RightButton:
                    self.data_model.add_coords_to_dataframe(
                        frame, bodypart, (np.nan, np.nan)
                    )

            self.update_scene()

        return super(Widget, self).eventFilter(obj, event)

    @property
    def current_bodypart_row(self):
        return self.bodyparts_view.currentRow()

    @current_bodypart_row.setter
    def current_bodypart_row(self, row):
        self.bodyparts_view.setCurrentRow(row)

    @property
    def current_frame_row(self):
        return self.frames_view.currentRow()

    @current_frame_row.setter
    def current_frame_row(self, row):
        self.frames_view.setCurrentRow(row)

    @property
    def current_bodypart_text(self):
        try:
            return self.bodyparts_view.currentItem().text()
        except AttributeError:
            return None

    @property
    def current_frame_text(self):
        try:
            return self.frames_view.currentItem().text()
        except AttributeError:
            return None

    def send_status(self, msg, timeout):
        self.parent().status_bar.showMessage(msg, timeout * 1000)

    def save_as_hdf(self):
        save_path = os.path.join(
            self.project_path, "CollectedData_{}.h5".format(self.config_dict["scorer"])
        )
        save_path = QFileDialog.getSaveFileName(dir=save_path)[0]
        self.data_model.save(save_path)

    def update_scene(self):
        # `frame` = `image_relpath`, which is a better name
        # TODO dedicated function for converting between rel and abs path

        def add_dots_to_scene(coords, size, brush_color, pen_color, tooltip):
            # Adds dots to the scene
            x, y = coords[0], coords[1]

            dot_rect = QRectF(x - size / 2, y - size / 2, size, size)
            dot_brush = QBrush(Qt.SolidPattern)
            dot_brush.setColor(brush_color)
            dot_pen = QPen(dot_brush, size / 40)
            dot_pen.setColor(pen_color)

            dot_ellipse = QGraphicsEllipseItem(dot_rect)
            dot_ellipse.setPen(dot_pen)
            dot_ellipse.setBrush(dot_brush)

            dot_ellipse.setToolTip(tooltip)

            self.graphics_view.scene.addItem(dot_ellipse)

        frame = self.current_frame_text

        if frame:
            self.graphics_view.scene.load_image(self.images_paths_dict[frame])

            dot_size = self.dot_size_slider.value()

            if self.data_model.data_frame is not None:
                for bodypart, brush_color, pen_color in zip(
                    self.bodyparts,
                    self.data_model.colors,
                    self.data_model.colors_opposite,
                ):
                    coords = self.data_model.get_coords_from_dataframe(frame, bodypart)
                    if not np.isnan(coords[0]):
                        add_dots_to_scene(
                            coords, dot_size, brush_color, pen_color, bodypart
                        )


class MainWindow(QMainWindow):
    """
    Define the main window and its menubar and statusbar
    """

    def __init__(self, config, app, scale_w, scale_h):
        super(MainWindow, self).__init__()

        self.setWindowTitle("DeepLabCut Labeling GUI")

        # Statusbar
        # must be defined before children for children to access it
        self.status_bar = self.statusBar()

        if config is None:
            config = QFileDialog.getOpenFileName(
                caption="Select config.yaml file", filter="(*.yaml)"
            )[0]
            if config == "":
                print("No config.yaml file provided, exiting...")
                sys.exit()

        widget = Widget(self, config)

        # Menubar
        open_frames_dir = QAction("Open directory of frames", self)
        open_frames_dir.setShortcut(QKeySequence("Ctrl+O"))
        open_frames_dir.triggered.connect(
            lambda x: widget.init_from_data_model_from_dir()
        )

        open_dataframe = QAction("Open *.h5 or *.hdf file", self)
        open_dataframe.setShortcut(QKeySequence("Ctrl+F"))
        open_dataframe.triggered.connect(
            lambda x: widget.init_from_data_model_from_file()
        )

        save_as_hdf = QAction("Save", self)
        save_as_hdf.setShortcut(QKeySequence("Ctrl+S"))
        save_as_hdf.triggered.connect(lambda x: widget.save_as_hdf())

        help_url = "https://dlc-gui.readthedocs.io/en/latest/README.html#using-the-gui"
        open_help = QAction("Help", self)
        open_help.setShortcut(QKeySequence("Ctrl+H"))
        open_help.triggered.connect(lambda x: webbrowser.open(help_url))

        self.menu_bar = self.menuBar()

        self.file_menu = self.menu_bar.addMenu("File")
        self.file_menu.addAction(open_frames_dir)
        self.file_menu.addAction(open_dataframe)
        self.file_menu.addAction(save_as_hdf)

        self.help_menu = self.menu_bar.addMenu("Help")
        self.help_menu.addAction(open_help)

        # Window dimensions
        geometry = app.desktop().availableGeometry(self)
        self.resize(geometry.width() * scale_w, geometry.height() * scale_h)
        self.setCentralWidget(widget)


def show(config=None, scale_w=0.8, scale_h=0.8):
    """
    Show the GUI.

    Parameters
    ----------
    config : str or None, optional (default None)
        The config.yaml file to use.
        May be None to use the GUI to pick the config.yaml file.
    scale_w, scale_h: float, optional (default 0.8)
        What portion of the display to set the main window's size to.

    """
    app = QApplication(sys.argv)
    window = MainWindow(config, app, scale_w, scale_h)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Abs path to config.yaml", nargs="?")
    args = parser.parse_args()
    config = args.config

    show(config)

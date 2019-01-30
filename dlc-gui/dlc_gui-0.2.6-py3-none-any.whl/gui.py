"""
This module handles all the GUI aspects of dlc_gui.

This module creates a main window containing the main widget containing subset widgets.
"""


# TODO fix bug of ghost tooltips
# TODO fix bug of clearing scene when canceling opening file

import os
import signal
import sys
import typing
import webbrowser

from PySide2.QtCore import QEvent, QRectF, Qt
from PySide2.QtGui import QBrush, QColor, QKeySequence, QPen, QPixmap
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QDesktopWidget,
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


import dlc_gui.data
import dlc_gui.util


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

    def zoom(self, pos: tuple, scale: float, anchor=None):
        if anchor is None:
            self.setTransformationAnchor(QGraphicsView.NoAnchor)
            self.setResizeAnchor(QGraphicsView.NoAnchor)

        old_pos = self.mapToScene(*pos)

        # Prevent zooming out beyond 0.3
        if self.scale_current > 0.3 or scale > 1:
            self.scale(scale, scale)
            self.scale_current *= scale

        new_pos = self.mapToScene(*pos)

        translate_delta = (new_pos - old_pos).toTuple()
        self.translate(*translate_delta)

    def wheelEvent(self, event):
        # Implement zooming with ctrl + mousewheel,
        # horizontal scrolling with shift + mousewheel,
        # and vertical scrolling with mousewheel

        # check which modifier key is held while wheel is scrolled
        modifiers = QApplication.keyboardModifiers()

        if modifiers == Qt.ControlModifier:
            scale_factor = 1.25
            if event.delta() > 0:
                self.zoom(event.pos().toTuple(), scale_factor)
            else:
                self.zoom(event.pos().toTuple(), 1 / scale_factor)
        elif modifiers == Qt.ShiftModifier:
            self.translate(event.delta(), 0)
        else:
            self.translate(0, event.delta())


class MainWidget(QWidget):
    """
    Create the main user interface and controls, connected to DataModel
    """

    def __init__(self, parent, config_path):
        super(MainWidget, self).__init__(parent)

        # Read config
        self.config_path = config_path
        self.config_dict = dlc_gui.util.read_config_file(self.config_path)
        # TODO move to data.py
        try:
            self.project_path = os.path.abspath(self.config_dict["project_path"])
        except TypeError as e:
            raise TypeError(
                "config.yaml defines 'project_path' as {0} of invalid type {1}.".format(
                    self.config_dict["project_path"],
                    type(self.config_dict["project_path"]),
                )
            ) from e

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
        data_model = dlc_gui.data.DataModel(self.config_path)
        self.init_from_data_model(data_model)

    def init_from_data_model_from_file(self, data_frame_file):
        data_model = dlc_gui.data.DataModel(self.config_path)
        try:
            data_model.init_from_file(data_frame_file)
        except (data_model.NoSuchNodeError, KeyError) as e:
            self.send_status(
                "Error: The .h5 file you picked is not structured correctly.", 5
            )
            raise e
        self.init_from_data_model(data_model)

    def init_from_data_model_from_dir(self, dir):
        data_model = dlc_gui.data.DataModel(self.config_path)
        data_model.init_from_dir(dir)
        if dir == "" or dir is None:
            pass
        elif not data_model.images_paths_dict:
            self.send_status(
                "Error: No images files (*.png) found in {}".format(dir), 5
            )
            # Recreate data_model object that isn't init-ed
            data_model = dlc_gui.data.DataModel(self.config_path)
            self.init_from_data_model(data_model)
        else:
            self.init_from_data_model(data_model)

    def init_from_data_model(self, data_model):

        self.data_model = data_model

        self.bodyparts = self.data_model.bodyparts

        # Populate the frames and bodyparts lists
        if self.data_model.images_paths_dict:
            self.images_paths_dict = self.data_model.images_paths_dict

            self.frames_view.clear()
            for frame in self.images_paths_dict.keys():
                self.frames_view.addItem(frame)

        self.bodyparts_view.clear()
        for bodypart in self.bodyparts:
            self.bodyparts_view.addItem(bodypart)

        # Convert tuples to QColors

        self.data_model.colors = [
            QColor.fromHsvF(*color) for color in self.data_model.colors
        ]
        self.data_model.colors_opposite = [
            QColor.fromHsvF(*color) for color in self.data_model.colors_opposite
        ]
        self.data_model.colors_opaque = [
            QColor.fromHsvF(*color) for color in self.data_model.colors_opaque
        ]

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
        """
        Implement left and right mouse clicking functionalities
        """
        # Check if the click is within the QGraphicsView
        if (
            obj is self.graphics_view.scene
            and event.type() == QEvent.Type.GraphicsSceneMousePress
        ):

            scene_pos = event.scenePos()
            coords = (scene_pos.x(), scene_pos.y())

            frame = self.current_frame_text
            bodypart = self.current_bodypart_text

            if frame and bodypart:
                if event.buttons() == Qt.LeftButton:
                    self.data_model.add_coords_to_dataframe(frame, bodypart, coords)
                elif event.buttons() == Qt.RightButton:
                    self.data_model.add_coords_to_dataframe(
                        frame, bodypart, (None, None)
                    )

            self.update_scene()

        return super(MainWidget, self).eventFilter(obj, event)

    @property
    def current_bodypart_row(self) -> int:
        return self.bodyparts_view.currentRow()

    @current_bodypart_row.setter
    def current_bodypart_row(self, row):
        self.bodyparts_view.setCurrentRow(row)

    @property
    def current_frame_row(self) -> int:
        return self.frames_view.currentRow()

    @current_frame_row.setter
    def current_frame_row(self, row):
        self.frames_view.setCurrentRow(row)

    @property
    def current_bodypart_text(self) -> typing.Union[str, None]:
        try:
            return self.bodyparts_view.currentItem().text()
        except AttributeError:
            return None

    @property
    def current_frame_text(self) -> typing.Union[str, None]:
        try:
            return self.frames_view.currentItem().text()
        except AttributeError:
            return None

    def send_status(self, msg, timeout):
        self.parent().status_bar.showMessage(msg, timeout * 1000)

    def save_as_pkl(self):
        save_path = os.path.join(
            self.project_path, "CollectedData_{}.pkl".format(self.config_dict["scorer"])
        )
        save_path = QFileDialog.getSaveFileName(dir=save_path)[0]
        self.data_model.save_as_pkl(save_path)

    def save_as_hdf(self):
        save_path = os.path.join(
            self.project_path, "CollectedData_{}.h5".format(self.config_dict["scorer"])
        )
        save_path = QFileDialog.getSaveFileName(dir=save_path)[0]
        self.data_model.save(save_path)

    # Updating scene is in MainWidget and not GraphicsScene because it needs to know
    # current frame and current bodypart, both properties of MainWidget
    def update_scene(self):
        # `frame` = `image_relpath`, which is a better name
        # TODO dedicated function for converting between rel and abs path

        def add_dots_to_scene(
            coords: tuple,
            size: float,
            brush_color: QColor,
            pen_color: QColor,
            tooltip: str,
        ):
            # Adds dots to the scene
            x, y = coords

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
                    if all(coord is not None for coord in coords):
                        add_dots_to_scene(
                            coords, dot_size, brush_color, pen_color, bodypart
                        )


class MainWindow(QMainWindow):
    """
    Define the main window and its menubar and statusbar
    """

    def __init__(self, config=None, relative_size=0.8):
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

        self.main_widget = MainWidget(self, config)

        # Menubar
        self.file_dialog = QFileDialog()
        self.file_dialog.setDirectory(self.main_widget.project_path)

        open_frames_dir = QAction("Open directory of frames", self)
        open_frames_dir.setShortcut(QKeySequence("Ctrl+O"))
        open_frames_dir.triggered.connect(
            lambda x: self.main_widget.init_from_data_model_from_dir(self.open_dir())
        )

        open_dataframe = QAction("Open *.h5 or *.pkl file", self)
        open_dataframe.setShortcut(QKeySequence("Ctrl+F"))
        open_dataframe.triggered.connect(
            lambda x: self.main_widget.init_from_data_model_from_file(
                QFileDialog.getOpenFileName(
                    dir=self.main_widget.project_path, filter="(*.hdf *.h5 *.pkl)"
                )[0]
            )
        )

        save_as_hdf = QAction("Save as .h5", self)
        save_as_hdf.setShortcut(QKeySequence("Ctrl+S"))
        save_as_hdf.triggered.connect(lambda x: self.main_widget.save_as_hdf())

        save_as_pkl = QAction("Save as .pkl", self)
        save_as_pkl.triggered.connect(lambda x: self.main_widget.save_as_pkl())

        help_url = "https://dlc-gui.readthedocs.io/en/latest/README.html#using-the-gui"
        open_help = QAction("Help", self)
        open_help.setShortcut(QKeySequence("Ctrl+H"))
        open_help.triggered.connect(lambda x: webbrowser.open(help_url))

        self.menu_bar = self.menuBar()

        self.file_menu = self.menu_bar.addMenu("File")
        self.file_menu.addAction(open_frames_dir)
        self.file_menu.addAction(open_dataframe)
        self.file_menu.addAction(save_as_hdf)
        self.file_menu.addAction(save_as_pkl)

        self.help_menu = self.menu_bar.addMenu("Help")
        self.help_menu.addAction(open_help)

        # Window dimensions
        self.resize(QDesktopWidget().availableGeometry(self).size() * relative_size)

        self.setCentralWidget(self.main_widget)

    def open_dir(self):
        self.file_dialog.setFileMode(QFileDialog.Directory)
        if self.file_dialog.exec():
            dir = self.file_dialog.selectedFiles()[0]
            return dir


def show(config=None, relative_size=0.8):
    """
    Show the GUI.

    Parameters
    ----------
    config : str or None, optional (default None)
        The config.yaml file to use.
        May be None to use the GUI to pick the config.yaml file.
    relative_size : float, optional (default 0.8)
        What portion of the display to set the main window's size to.

    """
    # Catch Ctrl+C to exit
    # TODO fix bug of hanging GUI when quitting
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    app = QApplication(sys.argv)
    window = MainWindow(config, relative_size)
    window.show()
    sys.exit(app.exec_())

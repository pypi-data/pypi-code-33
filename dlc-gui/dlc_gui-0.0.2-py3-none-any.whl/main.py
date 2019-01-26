"""
This is designed to be a reimplementation of the original labeling_toolbox.py
in Qt5 rather than WxPython. Its goal is to be user friendly and convenient.
"""

#TODO distinguish between 'bodypart' and 'label'
#TODO fix bug of unresponsive shortcuts of menubar

import sys
import os
import glob
import argparse

from PySide2.QtWidgets import (QWidget, QMainWindow, QApplication, QGridLayout,
                               QGraphicsScene, QGraphicsView, QListWidget,
                               QPushButton, QGraphicsEllipseItem, QFileDialog,
                               QAction, QTextBrowser, QLabel, QSplitter)
from PySide2.QtGui import (QPixmap, QPen, QBrush, QPainter, QImage, QColor,
                           QKeySequence)
from PySide2.QtCore import Qt, QRectF, QLineF, QPointF, QEvent

import yaml
import pandas as pd
import numpy as np


class DataModel:
    def __init__(self, config):

        self.config = config
        with open(config, 'r') as f:
            self.config_dict = yaml.load(f)

        self.scorer = self.config_dict['scorer']
        self.bodyparts = self.config_dict['bodyparts']
        self.project_path = self.config_dict['project_path']

        self.init_colors(len(self.bodyparts))

        #TODO find replacement for pd.concat to avoid defining variable as None
        self.data_frame = None
        self.images_paths_dict = {}

    def init_colors(self, number):
        hues = np.linspace(0, 1, number, endpoint=False)
        hsv_tuples = [(h, 1, 1) for h in hues]

        self.colors = []
        self.colors_opposite = []
        for hsv_tuple in hsv_tuples:
            h, s, v = [i for i in hsv_tuple]
            self.colors.append(QColor.fromHsvF(h, s, v, 0.5))
            h = abs(0.5 - h)
            self.colors_opposite.append(QColor.fromHsvF(h, s, v, 0.8))

    def init_from_dir(self, dir):
        self.images_paths = sorted(glob.glob(os.path.join(dir, '*.png')))

        if self.images_paths:
            init_nan = np.empty((len(self.images_paths), 2)).fill(np.nan)

            self.images_relpaths = [
                os.path.relpath(image_path, self.project_path)
                for image_path in self.images_paths
            ]

            self.images_paths_dict = dict(
                zip(self.images_relpaths, self.images_paths))

            for bodypart in self.bodyparts:
                index = pd.MultiIndex.from_product(
                    [[self.scorer], [bodypart], ['x', 'y']],
                    names=['scorer', 'bodyparts', 'coords'])
                frame = pd.DataFrame(
                    init_nan, columns=index, index=self.images_relpaths)
                self.data_frame = pd.concat([self.data_frame, frame], axis=1)

    def init_from_file(self, file):
        """
        Due to the inconsistencies between ``to_csv``, ``from_csv``, ``read_csv``, etc.,
        ONLY '.h5' files will be accepted.
        https://github.com/pandas-dev/pandas/issues/13262
        """

        if file:
            self.data_frame = pd.read_hdf(file, 'df_with_missing')

            # assumes structure, may not be reliable
            self.images_relpaths = sorted(self.data_frame.index.tolist()[2:])
            self.images_paths = [
                os.path.join(self.project_path, i)
                for i in self.images_relpaths
            ]

            #TODO avoid copy pasted code
            self.images_paths_dict = dict(
                zip(self.images_relpaths, self.images_paths))

    def write(self, frame, bodypart, coords):

        self.data_frame.loc[frame, self.scorer][bodypart, 'x'] = coords[0]
        self.data_frame.loc[frame, self.scorer][bodypart, 'y'] = coords[1]

    def get_coords_from_frame_and_bodypart(self, frame, bodypart):
        x = self.data_frame.loc[frame, self.scorer][bodypart, 'x']
        y = self.data_frame.loc[frame, self.scorer][bodypart, 'y']

        return tuple([x, y])

    def save(self, path):
        if path:
            self.data_frame.to_hdf(
                path, 'df_with_missing', format='table', mode='w')


class GraphicsScene(QGraphicsScene):
    def __init__(self, parent):
        super(GraphicsScene, self).__init__(parent)

    def load_image(self, image):
        """Loads an image into the scene"""
        self.frame_image = QPixmap()
        self.frame_image.load(image)
        self.addPixmap(self.frame_image)


class GraphicsView(QGraphicsView):
    def __init__(self, parent):
        super(GraphicsView, self).__init__(parent)

        self.scene = GraphicsScene(self)

        self.setScene(self.scene)
        self.fitInView(
            self.scene.sceneRect(), aspectRadioMode=Qt.KeepAspectRatio)

        self.viewport().setCursor(Qt.CrossCursor)

        # `scale_current` keeps track of the current scale value to prevent zooming too far out
        self.scale_current = 1.0

    def wheelEvent(self, event):
        """
        Implement zooming with ctrl + mousewheel,
        horizontal scrolling with shift + mousewheel,
        and vertical scrolling with mousewheel
        """

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
    def __init__(self, parent, config):
        super(Widget, self).__init__(parent)

        self.config = config
        with open(self.config, 'r') as f:
            self.config_dict = yaml.load(f)
        self.project_path = self.config_dict['project_path']

        with open(self.config, 'r') as f:
            self.frames_path = os.path.join(
                yaml.load(f)['project_path'], 'labeled-data')

        self.graphics_view = GraphicsView(self)
        self.labels_view = QListWidget()
        self.frames_view = QListWidget()

        main_layout = QGridLayout()
        splitter = QSplitter()

        splitter.addWidget(self.frames_view)
        splitter.addWidget(self.graphics_view)
        splitter.addWidget(self.labels_view)

        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        self.init_from_data_model_from_nothing()

        self.frames_view.currentItemChanged.connect(
            lambda x: self.update_scene())

        self.graphics_view.scene.installEventFilter(self)

    def get_current_frame(self):
        # Returns relpath of currently selected frame
        try:
            return self.frames_view.currentItem().text()
        except AttributeError:
            return None

    def get_current_bodypart(self):
        try:
            return self.labels_view.currentItem().text()
        except AttributeError:
            return None

    def send_status(self, msg, timeout):
        self.parent().status_bar.showMessage(msg, timeout * 1000)

    def save_to_hdf(self):
        save_path = os.path.join(
            self.project_path,
            'CollectedData_{}.h5'.format(self.config_dict['scorer']))
        save_path = QFileDialog.getSaveFileName(dir=save_path)[0]
        self.data_model.save(save_path)

    def init_from_data_model_from_nothing(self):
        data_model = DataModel(self.config)
        data_model.init_from_dir('')
        self.init_from_data_model(data_model)

    def init_from_data_model_from_file(self):
        data_model = DataModel(self.config)
        data_model.init_from_file(
            QFileDialog.getOpenFileName(
                dir=self.project_path, filter="(*.hdf *.h5)")[0])
        self.init_from_data_model(data_model)

    def init_from_data_model_from_dir(self):
        data_model = DataModel(self.config)
        dir = QFileDialog.getExistingDirectory(dir=self.project_path)
        data_model.init_from_dir(dir)
        if not data_model.images_paths_dict and dir:
            self.send_status('No images files (*.png) found in {}'.format(dir),
                             5)
        self.init_from_data_model(data_model)

    def init_from_data_model(self, data_model):

        self.data_model = data_model

        self.bodyparts = self.data_model.bodyparts

        if self.data_model.images_paths_dict:
            self.images_paths_dict = self.data_model.images_paths_dict

            self.frames_view.clear()
            for frame in self.images_paths_dict.keys():
                self.frames_view.addItem(frame)

        self.labels_view.clear()
        for bodypart in self.bodyparts:
            self.labels_view.addItem(bodypart)

        # Set initial selections for both listwidgets
        frames_view_items = self.frames_view.findItems('*', Qt.MatchWildcard)
        if frames_view_items:
            self.frames_view.setCurrentItem(frames_view_items[0])
            self.graphics_view.scene.load_image(
                list(self.images_paths_dict.values())[0])

        self.labels_view_items = self.labels_view.findItems(
            '*', Qt.MatchWildcard)
        if self.labels_view_items:
            self.labels_view.setCurrentItem(self.labels_view_items[0])
            for item, color in zip(self.labels_view_items,
                                   self.data_model.colors):
                #TODO remove copy-paste of extracting r, g, b from `color`
                item.setBackgroundColor(color)

        self.update_scene()

    def eventFilter(self, obj, event):
        if obj is self.graphics_view.scene and event.type(
        ) == QEvent.Type.GraphicsSceneMousePress:

            scene_pos = event.scenePos()
            coords = tuple([scene_pos.x(), scene_pos.y()])

            frame = self.get_current_frame()
            bodypart = self.get_current_bodypart()

            if frame and bodypart:
                if event.buttons() == Qt.LeftButton:
                    self.data_model.write(frame, bodypart, coords)
                elif event.buttons() == Qt.RightButton:
                    self.data_model.write(frame, bodypart, (np.nan, np.nan))

            self.update_scene()

            # Automatically cycle through labels and frames
            current_label_row = self.labels_view.currentRow()
            current_frame_row = self.frames_view.currentRow()

            self.labels_view.setCurrentRow(current_label_row + 1)

            if current_label_row == -1:
                self.labels_view.setCurrentRow(0)
                self.frames_view.setCurrentRow(current_frame_row + 1)

        return super(Widget, self).eventFilter(obj, event)

    def update_scene(self):
        """Important to remember that `frame` = `image_relpath`, which is a better name"""
        #TODO make function to convert relative to absolute path for explicit readability

        frame = self.get_current_frame()

        if frame:
            self.graphics_view.scene.load_image(self.images_paths_dict[frame])

            scene_size = self.graphics_view.scene.sceneRect()
            dot_size = (scene_size.height() + scene_size.width()) / 2 / 100

            if self.data_model.data_frame is not None:
                for bodypart, brush_color, pen_color in zip(
                        self.bodyparts, self.data_model.colors,
                        self.data_model.colors_opposite):
                    coords = self.data_model.get_coords_from_frame_and_bodypart(
                        frame, bodypart)
                    if not np.isnan(coords[0]):
                        self.add_dots(coords, dot_size, brush_color, pen_color,
                                      bodypart)

    def add_dots(self, coords, size, brush_color, pen_color, tooltip):
        """Adds dots to the scene"""
        #TODO different colors for each bodypart, and clear connection between the two

        x, y = coords[0], coords[1]

        self.dot_rect = QRectF(x - size / 2, y - size / 2, size, size)
        self.dot_brush = QBrush(Qt.SolidPattern)
        self.dot_brush.setColor(brush_color)
        self.dot_pen = QPen(self.dot_brush, size / 40)
        self.dot_pen.setColor(pen_color)

        self.dot_ellipse = QGraphicsEllipseItem(self.dot_rect)
        self.dot_ellipse.setPen(self.dot_pen)
        self.dot_ellipse.setBrush(self.dot_brush)

        self.dot_ellipse.setToolTip(tooltip)

        self.graphics_view.scene.addItem(self.dot_ellipse)


class HelpDialog(QWidget):
    def __init__(self):
        super(HelpDialog, self).__init__()

        help_text = """
        <style>
            table {
              border-collapse: collapse;
              width: 100%;
            }

            td, th {
              border: 1px solid #dddddd;
              text-align: left;
              padding: 8px;
            }

            tr:nth-child(even) {
              background-color: #dddddd;
            }
        </style>

        <h3>Keybindings</h3>
        <table style="width:100%">
            <tr>
                <th>Keybinding</th>
                <th>Action</th>
            </tr>
            <tr>
                <td>Left Mouse</td>
                <td>Add label at cursor</td>
            </tr>
            <tr>
                <td>Right Mouse</td>
                <td>Remove label</td>
            </tr>           <tr>
                <td>Ctrl + Mousewheel</td>
                <td>Zoom</td>
            </tr>
            <tr>
                <td>Shift + Mousewheel</td>
                <td>Horizontal Scroll</td>
            </tr>
            <tr>
                <td>Mousewheel</td>
                <td>Vertical Scroll</td>
            </tr>
        </table>

        <h3>Use</h3>
            <p>
            Begin by opening a directory full of the frames (*.png) you
            want to label, or a .h5 file from a previous save.
            <br><br>
            Use left mouse click to add a label at the cursor, or right mouse
            to remove a label. Switch between frame or bodypart using the left
            and right panels.
            <br><br>
            Save by pressing File > Save, or Ctrl+S. This will save your
            labeling as a .h5 file that can later be edited.
            </p>
        """

        label = QLabel('Help')
        label.setStyleSheet('font: 16pt')

        text_browser = QTextBrowser()
        text_browser.setHtml(help_text)

        button = QPushButton('Close')
        button.clicked.connect(lambda x: self.close())

        layout = QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(text_browser, 1, 0)
        layout.addWidget(button, 2, 0)
        self.setLayout(layout)

        self.setWindowFlags(Qt.Dialog)


class MainWindow(QMainWindow):
    def __init__(self, config, app, scale_w, scale_h):
        super(MainWindow, self).__init__()

        self.setWindowTitle("DeepLabCut Labeling GUI")

        # Statusbar
        # must be defined before children for children to access it
        self.status_bar = self.statusBar()

        if config is None:
            config = QFileDialog.getOpenFileName(
                caption='Select config.yaml file', filter="(*.yaml)")[0]

        widget = Widget(self, config)

        # Menubar
        open_frames_dir = QAction('Open directory of frames', self)
        open_frames_dir.setShortcut(QKeySequence('Ctrl+O'))
        open_frames_dir.triggered.connect(
            lambda x: widget.init_from_data_model_from_dir())

        open_dataframe = QAction('Open *.h5 or *.hdf file', self)
        open_dataframe.setShortcut(QKeySequence('Ctrl+F'))
        open_dataframe.triggered.connect(
            lambda x: widget.init_from_data_model_from_file())

        save_to_hdf = QAction('Save', self)
        save_to_hdf.setShortcut(QKeySequence('Ctrl+S'))
        save_to_hdf.triggered.connect(lambda x: widget.save_to_hdf())

        help_dialog = HelpDialog()

        help = QAction('Help', self)
        help.setShortcut(QKeySequence('Ctrl+H'))
        help.triggered.connect(lambda x: help_dialog.show())

        self.menu_bar = self.menuBar()

        self.file_menu = self.menu_bar.addMenu("File")
        self.file_menu.addAction(open_frames_dir)
        self.file_menu.addAction(open_dataframe)
        self.file_menu.addAction(save_to_hdf)

        self.help_menu = self.menu_bar.addMenu("Help")
        self.help_menu.addAction(help)

        # Window dimensions
        geometry = app.desktop().availableGeometry(self)
        self.resize(geometry.width() * scale_w, geometry.height() * scale_h)
        help_dialog.resize(geometry.width() * scale_w / 2,
                           geometry.height() * scale_h / 1.5)
        self.setCentralWidget(widget)


def main(config, scale_w, scale_h):
    app = QApplication(sys.argv)
    window = MainWindow(config, app, scale_w, scale_h)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('config', help='Abs path to config.yaml', nargs='?')
    args = parser.parse_args()
    config = args.config

    main(config, 0.8, 0.8)

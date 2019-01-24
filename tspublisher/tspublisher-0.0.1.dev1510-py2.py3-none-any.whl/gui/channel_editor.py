
from Qt import QtWidgets, QtCore

from publisher.gui.delegates import CheckBoxDelegate, ComboBoxDelegate
from publisher.procedure_content import build_channel_list, save_channel_changes
from publisher.processing.data_sources.organisation import get_data_from_channel
from publisher.processing.procedure import update_channel, build_channel
from publisher.settings import CHANNEL_TYPES

from .models import ChannelTableModel
from .ui.channel_editor import Ui_channel_editor
from .widgets import SpinnerOverlay


class ChannelEditor(QtWidgets.QWidget, Ui_channel_editor):

    def __init__(self, parent=None):
        super(ChannelEditor, self).__init__(parent)
        self.channel_model = ChannelTableModel(self)
        self.channel_model.validation_error.connect(self._display_error)
        self.setupUi(self)
        self.channel_tbl.addAction(self.add_row)
        self.channel_tbl.addAction(self.delete_row)
        self.channel_tbl.setModel(self.channel_model)
        self.channel_tbl.setItemDelegateForColumn(self.channel_model.header.index('eula_required'),
                                                  CheckBoxDelegate(self))
        self.channel_tbl.setItemDelegateForColumn(self.channel_model.header.index('type'),
                                                  ComboBoxDelegate(self, CHANNEL_TYPES))
        self.loading_overlay = SpinnerOverlay(self.channel_tbl)
        # Pyside vs PySide2 incompatability not managed correctly by Qt Shim
        if 'setSectionResizeMode' in dir(self.channel_tbl.horizontalHeader()):
            self.channel_tbl.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        else:
            self.channel_tbl.horizontalHeader().setResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.load_channel_data()

    @QtCore.Slot()
    def on_submit_btn_clicked(self):
        data = self.channel_model.edited_channels
        errors = self._validate_submit(data)
        if errors:
            self._display_error(errors)
            return
        message = self.msg.toPlainText()
        self.data_saver = SaveChannelDataWorker(data, message)
        self.data_saver.done.connect(self._on_write_completed)
        self.data_saver.error.connect(self._display_error)
        self.loading_overlay.show()
        self.data_saver.start()

    @QtCore.Slot()
    def on_add_row_triggered(self):
        data = {'code': '', 'name': '', 'type': CHANNEL_TYPES[0], 'eula_required': False, 'new': True}
        row = self.channel_tbl.selectedIndexes()[0].row()
        self.channel_model.add_channel(data, row)

    @QtCore.Slot()
    def on_delete_row_triggered(self):
        row = self.channel_tbl.selectedIndexes()[0].row()
        self.channel_model.delete_row(row)

    def load_channel_data(self):
        self._disable_input()
        self.loading_overlay.show()
        self.data_loader = LoadChannelDataWorker()
        self.data_loader.channel_data.connect(self.channel_model.add_channel)
        self.data_loader.done.connect(self._on_data_loaded)
        self.data_loader.start()

    def _on_data_loaded(self):
        self.loading_overlay.hide()
        self._enable_input()

    def _on_write_completed(self):
        self.loading_overlay.hide()
        self._enable_input()

    def _display_error(self, message):
        QtWidgets.QMessageBox.critical(self, "Error", "Error: {}".format(message))
        self.loading_overlay.hide()
        self._enable_input()

    def _enable_input(self):
        self.msg.setEnabled(True)
        self.channel_tbl.setEnabled(True)
        self.submit_btn.setEnabled(True)

    def _disable_input(self):
        self.msg.setEnabled(False)
        self.channel_tbl.setEnabled(False)
        self.submit_btn.setEnabled(False)

    def _validate_submit(self, data):
        if self.msg.toPlainText() == '':
            return "Submit comment must not be blank"
        for item in data:
            if not item.get('name'):
                return "Name is blank for channel with code {}".format(item.get('code'))
            if not item.get('code'):
                return "Code is blank for channel with name {}".format(item.get('name'))


class LoadChannelDataWorker(QtCore.QThread):

    channel_data = QtCore.Signal(dict)
    done = QtCore.Signal()

    def run(self):
        for channel in build_channel_list():
            data = get_data_from_channel(channel)
            self.channel_data.emit(data)
        self.done.emit()


class SaveChannelDataWorker(QtCore.QThread):

    done = QtCore.Signal()
    error = QtCore.Signal(str)

    def __init__(self, data, msg):
        try:
            self.data = data
            self.message = msg
            super(SaveChannelDataWorker, self).__init__()
        except Exception as e:
            message = str(e)
            self.error.emit(message)

    def run(self):
        try:
            for channel in self.data:
                if channel.get('new', False):
                    channel_data = {'code': channel['code'], 'name': channel['name'], 'type': channel['type'],
                                    'eula': channel['eula_required']}
                    build_channel(channel_data)
                else:
                    updates = {'name': channel['name'], 'type': channel['type'], 'eula': channel['eula_required']}
                    update_channel(channel['code'], updates)
            save_channel_changes(self.message)
            self.done.emit()
        except Exception as e:
            message = str(e)
            self.error.emit(message)

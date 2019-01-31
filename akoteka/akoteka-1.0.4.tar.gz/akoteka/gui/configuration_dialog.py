import sys
import os

from pkg_resources import resource_string, resource_filename

from akoteka.gui.pyqt_import import *

from akoteka.constants import *
from akoteka.handle_property import _
from akoteka.handle_property import config_ini

# ====================
#
# Configuration Dialog
#
# ====================
class ConfigurationDialog(QDialog):

    def __init__(self):
        super().__init__()    
    
        self.setWindowTitle(_('title_settings'))
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)

        self.self_layout = QVBoxLayout(self)
        self.self_layout.setSpacing(0)
        self.setLayout(self.self_layout)
        
        self.content_section = ContentSection()
        
        self.self_layout.addWidget(self.content_section)
                
        self.self_layout.addStretch(1)
        
        button_box_section = ButtonBoxSection(self)
        self.self_layout.addWidget(button_box_section)
        
        # language
        self.language_selector = LanguageSelector(config_ini['language'])
        self.content_section.addWidget(self.language_selector)
        
        # media path
        self.media_path_selector = MediaPathSelector(config_ini['media_path'])
        self.content_section.addWidget(self.media_path_selector)
        
        self.content_section.addWidget(QHLine())

        # video player 
        self.media_player_video_selector = MediaPlayerVideoSelector(config_ini['media_player_video'])
        self.content_section.addWidget(self.media_player_video_selector)
        
        # video player parameters        
        self.media_player_video_param = MediaPlayerVideoParam(config_ini['media_player_video_param'])
        self.content_section.addWidget(self.media_player_video_param)

        self.content_section.addWidget(QHLine())

        # audio player 
        self.media_player_audio_selector = MediaPlayerAudioSelector(config_ini['media_player_audio'])
        self.content_section.addWidget(self.media_player_audio_selector)
        
        # audio player parameters        
        self.media_player_audio_param = MediaPlayerAudioParam(config_ini['media_player_audio_param'])
        self.content_section.addWidget(self.media_player_audio_param)
    
    def get_media_path(self):
        return self.media_path_selector.get_media_path()
        
    def get_language(self):
        return self.language_selector.get_language()
 
    def get_media_player_video(self):
        return self.media_player_video_selector.get_media_player_video() 
    
    def get_media_player_video_param(self):
        return self.media_player_video_param.get_media_player_video_param()

    def get_media_player_audio(self):
        return self.media_player_audio_selector.get_media_player_audio() 
    
    def get_media_player_audio_param(self):
        return self.media_player_audio_param.get_media_player_audio_param()

class ContentSection(QWidget):
        def __init__(self):
            super().__init__()    
    
            self.self_layout = QVBoxLayout(self)
            self.self_layout.setSpacing(3)
            self.setLayout(self.self_layout)
        
        def addWidget(self, widget):
            self.self_layout.addWidget(widget)

class ButtonBoxSection(QWidget):
        def __init__(self, parent):
            super().__init__()    
    
            self.self_layout = QHBoxLayout(self)
            self.setLayout(self.self_layout)
            
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            self.self_layout.addWidget( button_box )

            button_box.button(QDialogButtonBox.Ok).setText(_('button_ok'))
            button_box.button(QDialogButtonBox.Cancel).setText(_('button_cancel'))
            button_box.accepted.connect(parent.accept)
            button_box.rejected.connect(parent.reject)
            

class LineTemplate(QWidget):
    def __init__(self, label):
        super().__init__()    
    
        self.self_layout=QHBoxLayout(self)
        self.self_layout.setContentsMargins(0,0,0,0)
        self.setStyleSheet("border:1px") 
        self.setLayout(self.self_layout)

        # Label
        label = QLabel(label)
        label.setMinimumWidth(LABEL_LENGTH)
        label.setMaximumWidth(LABEL_LENGTH)
        self.self_layout.addWidget(label)
        
# ====================
#
# Language Selector
#
# ====================
class LanguageSelector(LineTemplate):
    
    def __init__(self, default_language):
        super().__init__(_('title_language') + ':')
        
        self.language_combo = QComboBox()
        self.language_combo.addItem(_('lang_hu'), 'hu')
        self.language_combo.addItem(_('lang_en'), 'en')
        style_box = "QComboBox { max-width: " + LANGUAGE_DROPDOWN_LENGTH + "px; min-width: " + LANGUAGE_DROPDOWN_LENGTH + "px; border: 1px solid gray; border-radius: 5px; } QComboBox QAbstractItemView {color: black; border: 1px solid gray}"

        # drop-down menu         
        self.language_combo.setStyleSheet(style_box)
        self.self_layout.addStretch(1)
        self.self_layout.addWidget(self.language_combo)
        
        # empty space at the end
        self.empty_button = QPushButton()
        self.empty_button.setCheckable(False)
        empty_icon = QIcon()
        empty_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_EMPTY_BUTTON)) ), QIcon.Normal, QIcon.On)
        self.empty_button.setIcon( empty_icon )
        self.empty_button.setIconSize(QSize(IMG_SIZE,IMG_SIZE))
        self.self_layout.addWidget(self.empty_button)
        
        # select the language from config.ini file
        self.language_combo.setCurrentIndex( self.language_combo.findData(default_language) )
        
    def get_language(self):
        return self.language_combo.itemData( self.language_combo.currentIndex() )

# ====================
#
# Media Path Selector
#
# ====================
class MediaPathSelector(LineTemplate):
    
    def __init__(self, default_media_path):
        super().__init__(_('title_media_path') + ':')    

        # Text Field
        self.folder_field = QLineEdit(self)
        self.folder_field.setText(default_media_path)
        self.self_layout.addWidget(self.folder_field)
        
        # Button
        self.folder_selector_button = QPushButton()
        self.folder_selector_button.setCheckable(False)
        selector_icon = QIcon()
        selector_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_FOLDER_BUTTON)) ), QIcon.Normal, QIcon.On)
        self.folder_selector_button.setIcon( selector_icon )
        self.folder_selector_button.setIconSize(QSize(IMG_SIZE,IMG_SIZE))
        self.folder_selector_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.folder_selector_button.setStyleSheet("background:transparent; border:none") 
        self.folder_selector_button.clicked.connect(self.select_folder_button_on_click)

        self.self_layout.addWidget(self.folder_selector_button)

    def get_media_path(self):
        return self.folder_field.text()
    
    def select_folder_button_on_click(self):
        
#folder = QFileDialog.getExistingDirectory(self, _('title_select_media_path'), glob.media_path, QFileDialog.ShowDirsOnly)
        folder = QFileDialog.getExistingDirectory(self, _('title_select_media_path'), config_ini['media_path'], QFileDialog.ShowDirsOnly)
        
        if folder:
            self.folder_field.setText(folder)
        
# ====================
#
# Media Player Video
#
# ====================
class MediaPlayerVideoSelector(LineTemplate):
    
    def __init__(self, default_media_player_video_path):
        super().__init__(_('title_media_player_video') + ':')

        # Text Field
        self.file_field = QLineEdit(self)
        self.file_field.setText(default_media_player_video_path)
        self.self_layout.addWidget(self.file_field)
        
        # Button
        self.folder_selector_button = QPushButton()
        self.folder_selector_button.setCheckable(False)
        selector_icon = QIcon()
        selector_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_FOLDER_BUTTON)) ), QIcon.Normal, QIcon.On)
        self.folder_selector_button.setIcon( selector_icon )
        self.folder_selector_button.setIconSize(QSize(IMG_SIZE,IMG_SIZE))
        self.folder_selector_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.folder_selector_button.setStyleSheet("background:transparent; border:none") 
        self.folder_selector_button.clicked.connect(self.select_folder_button_on_click)

        self.self_layout.addWidget(self.folder_selector_button)

    def get_media_player_video(self):
        return self.file_field.text()
    
    def select_folder_button_on_click(self):        
        file, valami = QFileDialog.getOpenFileName(self, _('title_select_media_player_video'), os.path.abspath(os.sep))
        
        if file:
            self.file_field.setText(file)


# ========================
#
# Media Player Video Param
#
# ========================
class MediaPlayerVideoParam(LineTemplate):
    
    def __init__(self, default_media_player_video_param):
        super().__init__( _('title_media_player_video_param') + ':' )
    
        # Text Field
        self.folder_field = QLineEdit(self)
        self.folder_field.setText(default_media_player_video_param)
        self.self_layout.addWidget(self.folder_field)
        
        self.empty_button = QPushButton()
        self.empty_button.setCheckable(False)
        empty_icon = QIcon()
        empty_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_EMPTY_BUTTON)) ), QIcon.Normal, QIcon.On)
        self.empty_button.setIcon( empty_icon )
        self.empty_button.setIconSize(QSize(IMG_SIZE,IMG_SIZE))
        self.self_layout.addWidget(self.empty_button)

        
    def get_media_player_video_param(self):
        return self.folder_field.text()
    
# ====================
#
# Media Player Audio
#
# ====================
class MediaPlayerAudioSelector(LineTemplate):
    
    def __init__(self, default_media_player_audio_path):
        super().__init__(_('title_media_player_audio') + ':')

        # Text Field
        self.file_field = QLineEdit(self)
        self.file_field.setText(default_media_player_audio_path)
        self.self_layout.addWidget(self.file_field)
        
        # Button
        self.folder_selector_button = QPushButton()
        self.folder_selector_button.setCheckable(False)
        selector_icon = QIcon()
        selector_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_FOLDER_BUTTON)) ), QIcon.Normal, QIcon.On)
        self.folder_selector_button.setIcon( selector_icon )
        self.folder_selector_button.setIconSize(QSize(IMG_SIZE,IMG_SIZE))
        self.folder_selector_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.folder_selector_button.setStyleSheet("background:transparent; border:none") 
        self.folder_selector_button.clicked.connect(self.select_folder_button_on_click)

        self.self_layout.addWidget(self.folder_selector_button)

    def get_media_player_audio(self):
        return self.file_field.text()
    
    def select_folder_button_on_click(self):        
        file, valami = QFileDialog.getOpenFileName(self, _('title_select_media_player_audio'), os.path.abspath(os.sep))
        
        if file:
            self.file_field.setText(file)


# ========================
#
# Media Player Audio Param
#
# ========================
class MediaPlayerAudioParam(LineTemplate):
    
    def __init__(self, default_media_player_audio_param):
        super().__init__( _('title_media_player_audio_param') + ':' )
    
        # Text Field
        self.folder_field = QLineEdit(self)
        self.folder_field.setText(default_media_player_audio_param)
        self.self_layout.addWidget(self.folder_field)
        
        self.empty_button = QPushButton()
        self.empty_button.setCheckable(False)
        empty_icon = QIcon()
        empty_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_EMPTY_BUTTON)) ), QIcon.Normal, QIcon.On)
        self.empty_button.setIcon( empty_icon )
        self.empty_button.setIconSize(QSize(IMG_SIZE,IMG_SIZE))
        self.self_layout.addWidget(self.empty_button)

        
    def get_media_player_audio_param(self):
        return self.folder_field.text()

    
    
    

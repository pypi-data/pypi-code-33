import sys
import os
import importlib
from threading import Thread
from pkg_resources import resource_string, resource_filename
from functools import cmp_to_key
import locale

from cardholder.cardholder import CardHolder
from cardholder.cardholder import Card
from cardholder.cardholder import CollectCardsThread

from akoteka.gui.pyqt_import import *
from akoteka.gui.card_panel import CardPanel
from akoteka.gui.configuration_dialog import ConfigurationDialog

from akoteka.accessories import collect_cards
from akoteka.accessories import filter_key
from akoteka.accessories import clearLayout
from akoteka.accessories import FlowLayout


from akoteka.constants import *
from akoteka.setup.setup import getSetupIni

from akoteka.handle_property import _
from akoteka.handle_property import re_read_config_ini
from akoteka.handle_property import config_ini
from akoteka.handle_property import get_config_ini

class GuiAkoTeka(QWidget, QObject):
    
    def __init__(self):
        #super().__init__()  
        QWidget.__init__(self)
        QObject.__init__(self)
        
        self.actual_card_holder = None
        self.card_holder_history = []
        
        # most outer container, just right in the Main Window
        box_layout = QVBoxLayout(self)
        self.setLayout(box_layout)
        # controls the distance between the MainWindow and the added container: scrollContent
        box_layout.setContentsMargins(0, 0, 0, 0)
        box_layout.setSpacing(0)
    
        # control panel
        self.control_panel = ControlPanel(self)
        self.control_panel.set_back_button_method(self.restore_previous_holder)
        box_layout.addWidget( self.control_panel)
    
        # scroll_content where you can add your widgets - has scroll
        scroll = QScrollArea(self)
        box_layout.addWidget(scroll)
        scroll.setWidgetResizable(True)
        scroll_content = QWidget(scroll)
        scroll_content.setStyleSheet('background: ' + COLOR_MAIN_BACKGROUND)
        scroll.setFocusPolicy(Qt.NoFocus)
    
#        scroll_content = QWidget(self)
#        scroll_content.setStyleSheet('background: ' + COLOR_MAIN_BACKGROUND)
#        box_layout.addWidget(scroll_content)
#        scroll_layout = QVBoxLayout(scroll_content)
#        scroll_content.setLayout(scroll_layout)

        # layout of the content with margins
        scroll_layout = QVBoxLayout(scroll_content)        
        scroll.setWidget(scroll_content)        
        # vertical distance between cards - Vertical
        scroll_layout.setSpacing(5)
        # spaces between the added Widget and this top, right, bottom, left side
        scroll_layout.setContentsMargins(15,15,15,15)
        scroll_content.setLayout(scroll_layout)

        # -------------------------------
        # Title
        # -------------------------------
        self.hierarchy_title = HierarchyTitle(scroll_content, self)
        self.hierarchy_title.set_background_color(QColor(COLOR_CARDHOLDER_BACKGROUND))
        self.hierarchy_title.set_border_radius(RADIUS_CARDHOLDER)

        # -------------------------------
        # Here comes later the CardHolder
        # -------------------------------
        self.card_holder_panel = QWidget(scroll_content)
        
        scroll_layout.addWidget(self.hierarchy_title)
        scroll_layout.addWidget(self.card_holder_panel)
        scroll_layout.addStretch(1)
        
        self.card_holder_panel_layout = QVBoxLayout(self.card_holder_panel)
        self.card_holder_panel_layout.setContentsMargins(0,0,0,0)
        self.card_holder_panel_layout.setSpacing(0)

        self.back_button_listener = None

        # --- Window ---
        sp=getSetupIni()
        self.setWindowTitle(sp['name'] + '-' + sp['version'])    
        #self.setGeometry(300, 300, 300, 200)
        self.resize(900,600)
        self.center()
        self.show()    

    def center(self):
        """Aligns the window to middle on the screen"""
        fg=self.frameGeometry()
        cp=QDesktopWidget().availableGeometry().center()
        fg.moveCenter(cp)
        self.move(fg.topLeft())

    # --------------------------
    #
    # Start CardHolder
    #
    # --------------------------
    def startCardHolder(self):

        # Create the first Card Holder - 
        #self.go_down_in_hierarchy( [], "" )
        self.go_down_in_hierarchy() 

        # Retreive the media path
        paths = [config_ini['media_path']]
        
        # Start to collect the Cards from the media path
        self.actual_card_holder.startCardCollection(paths)        

    # --------------------------------------------------------------
    #
    # Go deeper in the hierarchy
    #
    # card_descriptor_structure The NOT Filtered card hierarchy list
    #                           on the recent level
    # title                     The title what whould be shown above
    #                           the CardHolder
    # save                      It controls to save the CardHolder
    #                           into the history list
    #                           collecting_finish uses it with False
    # --------------------------------------------------------------
    def go_down_in_hierarchy( self, card_descriptor_structure=None, title=None, save=True ):

        # if it is called very first time
        if card_descriptor_structure is None:
            self.initialize = True
            card_descriptor_structure = []
            title = ""
            save = False
        else:
            self.initialize = False

        # if there is already a CardHolder
        if self.actual_card_holder:

            # hide the old CardHolder
            self.actual_card_holder.setHidden(True)

        # if it is said to Save the CardHolder to the history list
        if save:
            
            # save the old CardHolder it in a list
            self.card_holder_history.append(self.actual_card_holder)
                    
        self.actual_card_holder = CardHolder(            
            self, 
            self.get_new_card,
            self.collect_cards,
            self.collecting_start,
            self.collecting_finish
        )
        
        self.actual_card_holder.title = title
        self.actual_card_holder.set_max_overlapped_cards( MAX_OVERLAPPED_CARDS )
        self.actual_card_holder.set_y_coordinate_by_reverse_index_method(self.get_y_coordinate_by_reverse_index)
        self.actual_card_holder.set_x_offset_by_index_method(self.get_x_offset_by_index)
        self.actual_card_holder.set_background_color(QColor(COLOR_CARDHOLDER_BACKGROUND))
        self.actual_card_holder.set_border_radius(RADIUS_CARDHOLDER)
        self.actual_card_holder.set_border_width(15)        
                
        # Save the original card desctiptor structure into the CardHolder
        self.actual_card_holder.orig_card_descriptor_structure = card_descriptor_structure
        
        # Make the CardHolder to be in Focus
        self.actual_card_holder.setFocus()

        # Set the title of the CardHolder - The actual level of the hierarchy
        self.hierarchy_title.set_title(self.card_holder_history, self.actual_card_holder)

        # add the new holder to the panel
        self.card_holder_panel_layout.addWidget(self.actual_card_holder)
        #self.scroll_layout.addStretch(1)
        
        # filter the list by the filters + Fill-up the CardHolder with Cards using the parameter as list of descriptor
        self.filter_the_cards(card_descriptor_structure)

    # -------------------------
    #
    # Come up in the hierarchy
    #
    # -------------------------
    def restore_previous_holder(self, steps=1):
        
        size = len(self.card_holder_history)
        if  size >= steps:

            for i in range(0, steps):
            
                previous_card_holder = self.card_holder_history.pop()
                # get the previous CardHolder
                #previous_card_holder = self.card_holder_history[size - 1]
            
                # remove the previous CardHolder from the history list
                #self.card_holder_history.remove(previous_card_holder)
            
            # hide the old CardHolder
            self.actual_card_holder.setHidden(True)            
            
            # remove from the layout the old CardHolder
            self.card_holder_panel_layout.removeWidget(self.actual_card_holder)
        
            # the current card holder is the previous
            self.actual_card_holder = previous_card_holder
            
            # show the current card holder
            self.actual_card_holder.setHidden(False)

            # set the title
            self.hierarchy_title.set_title(self.card_holder_history, self.actual_card_holder)
            
            # filter the list by the filters + Fill-up the CardHolder with Cards using the parameter as list of descriptor
            self.filter_the_cards(self.actual_card_holder.orig_card_descriptor_structure)
            
            # select the Card which was selected to enter
            self.actual_card_holder.select_actual_card()

    # ------------------
    # Collecting Started
    # ------------------
    def collecting_start(self):
        """
        Indicates that the CardCollection process started.
        The CardHolder calls this method
        Jobs to do:
            -Hide the title
        """
        self.hierarchy_title.setHidden(True)

    # -------------------
    # Collecting Finished
    # -------------------
    def collecting_finish(self, card_holder, card_descriptor_structure):
        """
        Indicates that the CardCollection process finished.
        The CardHolder calls this method
        Jobs to do:
            -Show the title
            -Set up the filters
        """        
        
        if card_descriptor_structure:
          
            # Show the title of the CardHolder (the certain level)        
            self.hierarchy_title.setHidden(False)
       
        
        # Save the NOT Filtered list
        card_holder.orig_card_descriptor_structure = card_descriptor_structure
        
        # Set-up the Filters        
        self.set_up_filters(card_descriptor_structure)
        
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # This part is tricky
        # It prevents to show the 0. level of Cards
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #
        # if there is only ONE Card and the status of the presentation is "initialize"
        if len(card_holder.card_descriptor_list) == 1 and self.initialize:
            # then I go down ONE level
            self.go_down_in_hierarchy(card_holder.card_descriptor_list[0]['extra']["orig-sub-cards"], card_holder.card_descriptor_list[0]['title'][config_ini['language']], save=False )

    # ----------------------------------------------------------
    #
    # Calculates the Y coordinate of a Card using reverse index
    #
    # ----------------------------------------------------------
    def get_y_coordinate_by_reverse_index(self, reverse_index, diff_to_max):
        raw_pos = (reverse_index + diff_to_max) * (reverse_index + diff_to_max)
        offset = diff_to_max * diff_to_max
        return (raw_pos - offset) * 8
        #return reverse_index * 220
    
    # -----------------------------------------------
    #
    # Calculates the X coordinate of a Card by index
    #
    # -----------------------------------------------
    def get_x_offset_by_index(self, index):
        return index * 4       

    def collect_cards(self, paths):
        cdl = collect_cards(paths)
        
        # Preparation for collecting the filtered_card_structure and filters
        filtered_card_structure = []
        filter_hit_list = {
            "genre": set(),
            "theme": set(),
            "director": set(),
            "actor": set(),
            "favorite": set(),
            "new": set(),
            "best": set()
        }
        self.generate_filtered_card_structure(cdl, filtered_card_structure, filter_hit_list)
        
        return filtered_card_structure
    
    # --------------------
    #
    # Generates a new Card
    #
    # --------------------
    def get_new_card(self, card_data, local_index, index):

        card = Card(self.actual_card_holder, card_data, local_index, index)
        
        if card_data["extra"]["media-path"]:
            card.set_background_color(QColor(COLOR_CARD_MOVIE_BACKGROUND))
        else:
            card.set_background_color(QColor(COLOR_CARD_COLLECTOR_BACKGROUND))
            
        card.set_border_normal_color(QColor(COLOR_CARD_BORDER_NORMAL_BACKGROUND))
        card.set_border_selected_color(QColor(COLOR_CARD_BORDER_SELECTED_BACKGROUND))
        
        card.set_not_selected()
        card.set_border_radius( RADIUS_CARD )
        card.set_border_width( WIDTH_BORDER_CARD )
 
        panel = card.get_panel()        
        layout = panel.get_layout()
        layout.setContentsMargins(0, 0, 0, 0)

        card_panel = CardPanel(card, card_data)
        layout.addWidget(card_panel)
        
        return card
  
    def set_filter_listener(self, listener):
        self.control_panel.set_filter_listener(listener)
        
    def get_filter_holder(self):
        return self.control_panel.get_filter_holder()
      
    # --------------------------------
    #
    # Filter the Cards
    #
    # Filters the Cards and Show them
    #
    # --------------------------------
    def filter_the_cards(self, card_descriptor_structure=None):
        if card_descriptor_structure is None:
            card_descriptor_structure = self.actual_card_holder.orig_card_descriptor_structure
        filtered_card_structure = self.set_up_filters(card_descriptor_structure)
        self.actual_card_holder.fillUpCardHolderByDescriptor(filtered_card_structure)

    # ----------------
    # Set-up Filters
    # ----------------
    def set_up_filters(self, card_descriptor_structure):
        """
        Based on the list that received as parameter, 
        it selects the possible filter elements
        """
        
        # ###################################
        # Turn OFF the listener to the Filter
        # ###################################
        self.set_filter_listener(None)
        
        # ####################################
        # Save the recent state of the filters
        # ####################################
        filters = {
            "genre": "",
            "theme": "",
            "director": "",
            "actor": "",
            "favorite": "",
            "new": "",
            "best": ""
        }
        for category, value in self.get_filter_holder().get_filter_selection().items():            
            if value != None and value != "":
                filters[category] = value
        
        # #############
        # Setup Filters
        # #############

        # Preparation for collecting the filtered_card_structure and filters
        filtered_card_structure = []
        filter_hit_list = {
            "genre": set(),
            "theme": set(),
            "director": set(),
            "actor": set(),
            "favorite": set(),
            "new": set(),
            "best": set()
        }
        self.generate_filtered_card_structure(card_descriptor_structure, filtered_card_structure, filter_hit_list)
        
        # Fill up GENRE dropdown
        self.get_filter_holder().clear_genre()
        self.get_filter_holder().add_genre("", "")

        for element in sorted([(_("genre_" + e),e) for e in filter_hit_list['genre']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.get_filter_holder().add_genre(element[0], element[1])
        
        # Fill up THEME dropdown
        self.get_filter_holder().clear_theme()
        self.get_filter_holder().add_theme("", "")
        for element in sorted([(_("theme_" + e), e) for e in filter_hit_list['theme']], key=lambda t: locale.strxfrm(t[0]) ):            
            self.get_filter_holder().add_theme(element[0], element[1])

        # Fill up DIRECTOR dropdown
        self.get_filter_holder().clear_director()
        self.get_filter_holder().add_director("")
        for element in sorted( filter_hit_list['director'], key=cmp_to_key(locale.strcoll) ):
            self.get_filter_holder().add_director(element)

        # Fill up ACTOR dropdown
        self.get_filter_holder().clear_actor()
        self.get_filter_holder().add_actor("")
        for element in sorted( filter_hit_list['actor'], key=cmp_to_key(locale.strcoll) ):
            self.get_filter_holder().add_actor(element)
        
        # ####################
        # Reselect the Filters
        # ####################
        self.get_filter_holder().select_genre(filters["genre"])
        self.get_filter_holder().select_theme(filters["theme"])
        self.get_filter_holder().select_director(filters["director"])
        self.get_filter_holder().select_actor(filters["actor"])
        
        # #######################################
        # Turn back ON the listener to the Filter
        # #######################################
        self.set_filter_listener(self)

        return filtered_card_structure
    
    
    # ================================
    # 
    # Generates Filtered CardStructure
    #
    # ================================   
    def generate_filtered_card_structure(self, card_structure, filtered_card_structure, filter_hit_list):
        """
        This method serves a dual task:
            -Based on the Filter it generates a new, filtered list: filtered_card_structure
            -Collects the new Filter, based on the filtered list:   filter_hit_list
        """
        mediaFits = False
        collectorFits = False
            
        # through the SORTED list
        for crd in sorted(card_structure, key=lambda arg: arg['title'][config_ini['language']], reverse=False):
            
            card = {}
            card['title'] = crd['title']
            card['storyline'] = crd['storyline']
            card['general'] = crd['general']
            card['rating'] = crd['rating']
            card['links'] = crd['links']

            card['extra'] = {}            
            card['extra']['image-path'] = crd['extra']['image-path']
            card['extra']['media-path'] = crd['extra']['media-path']
            card['extra']['recent-folder'] = crd['extra']['recent-folder']            
            card['extra']['sub-cards'] = [] #json.loads('[]')
            card['extra']['orig-sub-cards'] = crd['extra']['sub-cards']

            # in case of MEDIA CARD
            if crd['extra']['media-path']:

                fits = True
                
                # go through the filters
                for category, value in self.get_filter_holder().get_filter_selection().items():
            
                    # if the specific filter is set
                    if value != None and value != "":

                        if filter_key[category]['store-mode'] == 'v':
                            if value != crd[filter_key[category]['section']][category]:
                                fits = False
                                
                        elif filter_key[category]['store-mode'] == 'a':
                            if value not in crd[filter_key[category]['section']][category]:
                                fits = False
                        else:
                            fits = False

                # let's keep this MEDIA CARD as it fits
                if fits:

                    # Collect the filters
                    for category, value in self.get_filter_holder().get_filter_selection().items():
                        if filter_key[category]['store-mode'] == 'v':
                            if card[filter_key[category]['section']][category]:
                                filter_hit_list[category].add(card[filter_key[category]['section']][category])
                                
                        elif filter_key[category]['store-mode'] == 'a':
                            for cat in card[filter_key[category]['section']][category]:
                                if cat.strip():
                                    filter_hit_list[category].add(cat.strip())
                    
                    filtered_card_structure.append(card)                    
                    mediaFits = True
                    
            # in case of COLLECTOR CARD
            else:                     
                     
                # then it depends on the next level
                fits = self.generate_filtered_card_structure(crd['extra']['sub-cards'], card['extra']['sub-cards'], filter_hit_list)
                
                if fits:
                    filtered_card_structure.append(card)
                    collectorFits = True
        
        return (mediaFits or collectorFits)
  
    # ----------------------------
    #
    # Key Press Event: Enter/Space
    #
    # ----------------------------
    def keyPressEvent(self, event):

        #
        # Enter / Return / Space
        #
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter or event.key() == Qt.Key_Space:

            # Simulate a Mouse Press / Release Event on the Image
            if self.actual_card_holder.shown_card_list and len(self.actual_card_holder.shown_card_list) > 0:
                card=self.actual_card_holder.shown_card_list[0]
                if card.is_selected():
                    
                    event_press = QMouseEvent(QEvent.MouseButtonPress, QPoint(10,10), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
                    event_release = QMouseEvent(QEvent.MouseButtonRelease, QPoint(10,10), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)

                    layout=card.get_panel().get_layout()                    
                    card_panel = layout.itemAt(0).widget()
                    card_panel.card_image.mousePressEvent(event_press)
                    card_panel.card_image.mouseReleaseEvent(event_release)            

        #
        # Escape
        #
        if event.key() == Qt.Key_Escape:
            self.restore_previous_holder()

        event.ignore()
  

class LinkLabel(QLabel):
    def __init__(self, text, parent, index):
        QLabel.__init__(self, text, parent)
        self.parent = parent
        self.index = index        
        self.setFont(QFont( FONT_TYPE, HIERARCHY_TITLE_FONT_SIZE, weight=QFont.Bold if index else QFont.Normal))

    # Mouse Hover in
    def enterEvent(self, event):
        if self.index:
            QApplication.setOverrideCursor(Qt.PointingHandCursor)
        event.ignore()

    # Mouse Hover out
    def leaveEvent(self, event):
        if self.index:
            QApplication.restoreOverrideCursor()
        event.ignore()

    # Mouse Press
    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.index:
            self.parent.panel.restore_previous_holder(self.index)
        event.ignore()
    

# =========================================
# 
# This Class represents the title
#
# =========================================
#
class HierarchyTitle(QWidget):
    DEFAULT_BACKGROUND_COLOR = Qt.lightGray
    DEFAULT_BORDER_RADIUS = 10
    
    def __init__(self, parent, panel):
        QWidget.__init__(self, parent)

        self.panel = panel
        
        self_layout = QHBoxLayout(self)
        self_layout.setContentsMargins(5, 5, 5, 5)
        self_layout.setSpacing(0)
        #self_layout.setAlignment(Qt.AlignHCenter)
        self.setLayout(self_layout)

        self.text = QWidget(self)
        #self.text.setWordWrap(True)
        #self.text.setAlignment(Qt.AlignHCenter)
        #self.text.setFont(QFont( FONT_TYPE, HIERARCHY_TITLE_FONT_SIZE, weight=QFont.Bold))
        self_layout.addWidget(self.text)
        
        #self.text_layout = FlowLayout(self.text)
        self.text_layout = QVBoxLayout(self.text)
        self.text_layout.setContentsMargins(0, 0, 0, 0)
        self.text_layout.setSpacing(0)
        self.text.setLayout(self.text_layout)

        self.set_background_color(QColor(HierarchyTitle.DEFAULT_BACKGROUND_COLOR), False)
        self.set_border_radius(HierarchyTitle.DEFAULT_BORDER_RADIUS, False)
        
        self.card_holder_history = None
        self.actual_card_holder = None
        self.no_refresh = False
        
#    def resizeEvent(self, event):
#        if not self.no_refresh:
#            self.refresh_title()
#        event.accept()
    
    def refresh_title(self):
        if self.card_holder_history and self.actual_card_holder:
            self.set_title(self.card_holder_history, self.actual_card_holder)
    
    def set_title(self, card_holder_history, actual_card_holder):
        #self.blockSignals(True)
        #self.no_refresh = True

        clearLayout(self.text_layout)
 
        self.card_holder_history = card_holder_history
        self.actual_card_holder = actual_card_holder
 
        history = []
        for index, card in enumerate(card_holder_history):
            if card.title:
                label = LinkLabel(card.title, self, len(card_holder_history)-index)
                history.append(label)
       
        minimumWidth = 0
        max_width = self.size().width() - 2 * 5        
        self.create_one_line_container()
        
        for cw in history:
            
            minimumWidth += self.get_width_in_pixels(cw)
            if minimumWidth <= max_width:            
                self.add_to_one_line_container(cw)
            else:
                self.push_new_line_container()
                self.create_one_line_container()
                minimumWidth = 0
                self.add_to_one_line_container(cw)
            
            separator = QLabel(' > ')
            separator.setFont(QFont( FONT_TYPE, HIERARCHY_TITLE_FONT_SIZE, weight=QFont.Normal ))
            minimumWidth += self.get_width_in_pixels(separator)
            if minimumWidth <= max_width:            
                self.add_to_one_line_container(separator)
            else:
                self.push_new_line_container()
                self.create_one_line_container()
                minimumWidth = 0
                self.add_to_one_line_container(separator)
                                       
        notLinkTitle = LinkLabel(actual_card_holder.title, self, 0)
        minimumWidth += self.get_width_in_pixels(notLinkTitle)
        if minimumWidth <= max_width:            
            self.add_to_one_line_container(notLinkTitle)
        else:
            self.push_new_line_container()
            self.create_one_line_container()
            minimumWidth = 0
            self.add_to_one_line_container(notLinkTitle)
        self.push_new_line_container()
       
        #self.no_refresh = False
        
        #self.blockSignals(False)
       
        #print(self.panel.size().width(), minimumWidth)
        #self.text_layout.addWidget(LinkLabel(actual_card_holder.title, self, 0))
        #print(self.panel.size().width())
        #print()



    def create_one_line_container(self):
        self.one_line_container = QWidget(self)
        self.one_line_container_layout = QHBoxLayout(self.one_line_container)
        self.one_line_container_layout.setContentsMargins(0, 0, 0, 0)
        self.one_line_container_layout.setSpacing(0)
        self.one_line_container.setLayout(self.one_line_container_layout)
        self.one_line_container_layout.setAlignment(Qt.AlignHCenter)

    def add_to_one_line_container(self, cw):
        self.one_line_container_layout.addWidget(cw)
        
    def push_new_line_container(self):
        self.text_layout.addWidget(self.one_line_container)
        
    def get_width_in_pixels(self, cw):
        initialRect = cw.fontMetrics().boundingRect(cw.text());
        improvedRect = cw.fontMetrics().boundingRect(initialRect, 0, cw.text());   
        return improvedRect.width()
        
        
    def set_background_color(self, color, update=False):
        self.background_color = color
        self.text.setStyleSheet('background: ' + color.name()) 
        if update:
            self.update()
            
    def set_border_radius(self, radius, update=True):
        self.border_radius = radius
        if update:
            self.update()            
        
    def paintEvent(self, event):
        s = self.size()
        qp = QPainter()
        qp.begin(self)
        qp.setRenderHint(QPainter.Antialiasing, True)
        qp.setBrush( self.background_color )

        qp.drawRoundedRect(0, 0, s.width(), s.height(), self.border_radius, self.border_radius)
        qp.end()
        
        

# =========================================
#
#          Control Panel 
#
# on the TOP of the Window
#
# Contains:
#           Back Button
#           Filter
#
# =========================================
class ControlPanel(QWidget):
    def __init__(self, gui):
        super().__init__()
       
        self.gui = gui
        
        self_layout = QHBoxLayout(self)
        self.setLayout(self_layout)
        
        # controls the distance between the MainWindow and the added container: scrollContent
        self_layout.setContentsMargins(3, 3, 3, 3)
        self_layout.setSpacing(5)

        # -------------
        #
        # Back Button
        #
        # -------------     
        self.back_button_method = None
        back_button = QPushButton()
        back_button.setFocusPolicy(Qt.NoFocus)
        back_button.clicked.connect(self.back_button_on_click)
        
        back_button.setIcon( QIcon( resource_filename(__name__,os.path.join("img", IMG_BACK_BUTTON)) ))
        back_button.setIconSize(QSize(32,32))
        back_button.setCursor(QCursor(Qt.PointingHandCursor))
        back_button.setStyleSheet("background:transparent; border:none") 

        # Back button on the left
        self_layout.addWidget( back_button )

        self_layout.addStretch(1)
        
        # -------------------
        #
        # Config Button
        #
        # -------------------
        self.config_button = QPushButton()
        self.config_button.setFocusPolicy(Qt.NoFocus)
        self.config_button.setCheckable(False)
        self.config_button.clicked.connect(self.config_button_on_click)
        
        config_icon = QIcon()
        config_icon.addPixmap(QPixmap( resource_filename(__name__,os.path.join("img", IMG_CONFIG_BUTTON)) ), QIcon.Normal, QIcon.On)
        self.config_button.setIcon( config_icon )
        self.config_button.setIconSize(QSize(25,25))
        self.config_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.config_button.setStyleSheet("background:transparent; border:none") 
        self_layout.addWidget( self.config_button )
        
        
        
        # -------------
        #
        # Filter Holder
        #
        # -------------
        self.filter_holder = FilterHolder()
        self.filter_holder.changed.connect(self.filter_on_change)
        
        # Filter on the right
        self_layout.addWidget(self.filter_holder)

        # Listeners
        self.back_button_listener = None
        self.filter_listener = None

    def refresh_label(self):
        self.filter_holder.refresh_label()

    def set_back_button_method(self, method):
        self.back_button_method = method
        
    def set_filter_listener(self, listener):
        self.filter_listener = listener
        
    def back_button_on_click(self):
        if self.back_button_method:
            self.back_button_method()


    # -----------------------
    #
    # Config Button Clicked
    #
    # -----------------------
    def config_button_on_click(self):

        dialog = ConfigurationDialog()

        # if OK was clicked
        if dialog.exec_() == QDialog.Accepted:        

            # get the values from the DIALOG
            l = dialog.get_language()
            mp = dialog.get_media_path()
            vp = dialog.get_media_player_video()
            vpp = dialog.get_media_player_video_param()
            ap = dialog.get_media_player_audio()
            app = dialog.get_media_player_audio_param()

            # Update the config.ini file
            config_ini_function = get_config_ini()
            config_ini_function.set_media_path(mp) 
            config_ini_function.set_language(l)
            config_ini_function.set_media_player_video(vp)
            config_ini_function.set_media_player_video_param(vpp)
            config_ini_function.set_media_player_audio(ap)
            config_ini_function.set_media_player_audio_param(app)


#!!!!!!!!!!!!
            # Re-read the config.ini file
            re_read_config_ini()

            # Re-import card_holder_pane
            mod = importlib.import_module("akoteka.gui.card_panel")
            importlib.reload(mod)
#!!!!!!!!!!!!

            # remove history
            for card_holder in self.gui.card_holder_history:
                card_holder.setHidden(True)
                self.gui.card_holder_panel_layout.removeWidget(card_holder)
                #self.gui.scroll_layout.removeWidget(card_holder)
            self.gui.card_holder_history.clear()
                
            # Remove recent CardHolder as well
            self.gui.actual_card_holder.setHidden(True)
            self.gui.card_holder_panel_layout.removeWidget(self.gui.actual_card_holder)
            self.gui.actual_card_holder = None
            
            # reload the cards
            self.gui.startCardHolder()
            
            # refresh the Control Panel
            self.refresh_label()
            
        dialog.deleteLater()
 
    def filter_on_change(self):
        if self.filter_listener:
            self.filter_listener.filter_the_cards()
    
    def get_filter_holder(self):
        return self.filter_holder









# ================
#
# Dropdown HOLDER
#
# ================
class FilterDropDownHolder(QWidget):
    
    def __init__(self):
        super().__init__()

        self.self_layout = QVBoxLayout(self)
        self.setLayout( self.self_layout )
        self.self_layout.setContentsMargins(0, 0, 0, 0)
        self.self_layout.setSpacing(1)

#        self.setStyleSheet( 'background: green')

    def add_dropdown(self, filter_dropdown):
        self.self_layout.addWidget(filter_dropdown)

# =============================
#
# Filter Drop-Down Simple
#
# =============================
#
class FilterDropDownSimple(QWidget):
    
    state_changed = pyqtSignal()
    
    def __init__(self, label):
        super().__init__()

        self_layout = QHBoxLayout(self)
        self_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout( self_layout )
#        self.setStyleSheet( 'background: green')
        
        self.label_widget = QLabel(label)
        self_layout.addWidget( self.label_widget )

        self.dropdown = QComboBox(self)
        self.dropdown.setFocusPolicy(Qt.NoFocus)
        #self.dropdown.setEditable(True)
        
        self.dropdown.currentIndexChanged.connect(self.current_index_changed)

        # TODO does not work to set the properties of the dropdown list. find out and fix
        style =             '''
            QComboBox { max-width: 200px; min-width: 200px; min-height: 15px; max-height: 15px;}
            QComboBox QAbstractItemView::item { min-width:100px; max-width:100px; min-height: 150px;}
            QListView::item:selected { color: red; background-color: lightgray; min-width: 1000px;}"
            '''            

        style_down_arrow = '''
            QComboBox::down-arrow { 
                image: url( ''' + resource_filename(__name__,os.path.join("img", "back-button.jpg")) + ''');
                
            }
        '''
        style_box = '''
            QComboBox { 
                max-width: 200px; min-width: 200px; border: 1px solid gray; border-radius: 5px;
            }
        '''
#       max-width: 200px; min-width: 200px; min-height: 1em; max-height: 1em; border: 1px solid gray; border-radius: 5px;
        
        style_drop_down ='''
            QComboBox QAbstractItemView::item { 
                color: red;
                max-height: 15px;
            }
        '''            
      
        self.dropdown.setStyleSheet(style_box + style_drop_down)
        self.dropdown.addItem("")

        self_layout.addWidget( self.dropdown )
    
    def clear_elements(self):
        self.dropdown.clear()

    def add_element(self, value, id):
        self.dropdown.addItem(value, id)

    # -------------------------------------
    # get the index of the selected element
    # -------------------------------------
    def get_selected_index(self):
        return self.dropdown.itemData( self.dropdown.currentIndex() )

    # -------------------------------------
    # get the value of the selected element
    # -------------------------------------
    def get_selected_value(self):
        return self.dropdown.itemText( self.dropdown.currentIndex() )
    
    def select_element(self, id):
        self.dropdown.setCurrentIndex( self.dropdown.findData(id) )

    def current_index_changed(self):
        self.state_changed.emit()
        
    def refresh_label(self, new_label):
        self.label_widget.setText(new_label)


# ==========
#
# CheckBox
#
# ==========
class FilterCheckBox(QCheckBox):
    def __init__(self, label):
        super().__init__(label)

        self.setLayoutDirection( Qt.RightToLeft )
        style_checkbox = '''
            QCheckBox { 
                min-height: 15px; max-height: 15px; border: 0px solid gray;
            }
        '''
        self.setStyleSheet( style_checkbox )
#        self.setFocusPolicy(Qt.NoFocus)

    def is_checked(self):
        return 'y' if self.isChecked() else None        
 
    def refresh_label(self, new_label):
        self.setText(new_label)


# ================
#
# Checkbox HOLDER
#
# ================
class FilterCheckBoxHolder(QWidget):
    
    def __init__(self):
        super().__init__()

        self.self_layout = QVBoxLayout(self)
        self.setLayout( self.self_layout )
        self.self_layout.setContentsMargins(0, 0, 0, 0)
        self.self_layout.setSpacing(1)

        #self.setStyleSheet( 'background: green')
        
    def add_checkbox(self, filter_checkbox):
        self.self_layout.addWidget(filter_checkbox)
        

# ===============
#
# Filter HOLDER
#
# ===============
class FilterHolder(QWidget):
    
    changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()

        self_layout = QHBoxLayout(self)
        self.setLayout( self_layout )
        self_layout.setContentsMargins(0, 0, 0, 0)
        self_layout.setSpacing(8)    
        
        # ----------
        #
        # Checkboxes
        #
        # ----------
        self.filter_cb_favorite = FilterCheckBox(_('title_favorite'))
        self.filter_cb_best = FilterCheckBox(_('title_best'))
        self.filter_cb_new = FilterCheckBox(_('title_new'))
                
        holder_checkbox = FilterCheckBoxHolder()
        
        holder_checkbox.add_checkbox(self.filter_cb_favorite)
        holder_checkbox.add_checkbox(self.filter_cb_best)
        holder_checkbox.add_checkbox(self.filter_cb_new)        
                
        # Listener
        self.filter_cb_favorite.stateChanged.connect(self.state_changed)
        self.filter_cb_best.stateChanged.connect(self.state_changed)
        self.filter_cb_new.stateChanged.connect(self.state_changed)
                        
        self_layout.addWidget(holder_checkbox)

        # ----------
        #
        # Dropdowns 
        #
        # ----------

        #
        # Dropdown - genre+theme
        #
        self.filter_dd_genre = FilterDropDownSimple(_('title_genre'))
        self.filter_dd_theme = FilterDropDownSimple(_('title_theme'))
        
        holder_dropdown_gt = FilterDropDownHolder()
        
        holder_dropdown_gt.add_dropdown(self.filter_dd_genre)
        holder_dropdown_gt.add_dropdown(self.filter_dd_theme)
        
        self_layout.addWidget(holder_dropdown_gt)

        #
        # Dropdown - director+actor
        #
        self.filter_dd_director = FilterDropDownSimple(_('title_director'))
        self.filter_dd_actor = FilterDropDownSimple(_('title_actor'))
        
        holder_dropdown_da = FilterDropDownHolder()
        
        holder_dropdown_da.add_dropdown(self.filter_dd_director)
        holder_dropdown_da.add_dropdown(self.filter_dd_actor)
        
        self_layout.addWidget(holder_dropdown_da)


        #mydd = QComboBox(self)
        #self_layout.addWidget(mydd)
        #mydd.setEditable(True)



        # Listeners
        self.filter_dd_genre.state_changed.connect(self.state_changed)
        self.filter_dd_theme.state_changed.connect(self.state_changed)
        self.filter_dd_director.state_changed.connect(self.state_changed)
        self.filter_dd_actor.state_changed.connect(self.state_changed)

    def refresh_label(self):
        self.filter_dd_genre.refresh_label(_('title_genre'))
        self.filter_dd_theme.refresh_label(_('title_theme'))
        self.filter_dd_director.refresh_label(_('title_director'))
        self.filter_dd_actor.refresh_label(_('title_actor'))
        self.filter_cb_favorite.refresh_label(_('title_favorite'))
        self.filter_cb_new.refresh_label(_('title_new'))
        self.filter_cb_best.refresh_label(_('title_best'))
        
        
    def clear_genre(self):
        self.filter_dd_genre.clear_elements()
        
    def add_genre(self, value, id):
        self.filter_dd_genre.add_element(value, id)
        
    def select_genre(self, id):
        self.filter_dd_genre.select_element(id)

    def clear_theme(self):
        self.filter_dd_theme.clear_elements()

    def add_theme(self, value, id):
        self.filter_dd_theme.add_element(value, id)
        
    def select_theme(self, id):
        self.filter_dd_theme.select_element(id)        

    def clear_director(self):
        self.filter_dd_director.clear_elements()
    
    def add_director(self, director):
        self.filter_dd_director.add_element(director, director)
    
    def select_director(self, id):
        self.filter_dd_director.select_element(id)
        
    def clear_actor(self):
        self.filter_dd_actor.clear_elements()

    def add_actor(self, actor):
        self.filter_dd_actor.add_element(actor, actor)
        
    def select_actor(self, id):
        self.filter_dd_actor.select_element(id)        
    
    def get_filter_selection(self):
        filter_selection = {
            "best": self.filter_cb_best.is_checked(),
            "new": self.filter_cb_new.is_checked(),
            "favorite": self.filter_cb_favorite.is_checked(),
            "genre": self.filter_dd_genre.get_selected_index(),
            "theme": self.filter_dd_theme.get_selected_index(),
            "director": self.filter_dd_director.get_selected_value(),
            "actor": self.filter_dd_actor.get_selected_value()
        }
        return filter_selection
    
    def state_changed(self):
        self.changed.emit()

    def closeEvent(self, event):
        print('close filter holder')














        
def main():   
    
    app = QApplication(sys.argv)
    ex = GuiAkoTeka()
    ex.startCardHolder()
    sys.exit(app.exec_())
    
    

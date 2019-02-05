#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#########################################################
# Name: mainwindow.py
# Porpose: main_frame
# Compatibility: Python3
# Platform: all
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2015-2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Created: 1 Feb. 2019
# Rev (00)

# This file is part of DrumsT.

#    DrumsT is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    DrumsT is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with DrumsT. If not, see <http://www.gnu.org/licenses/>.
#########################################################
#
import wx
from src.drumsT_DIALOGS import add_student
from src.drumsT_DIALOGS import add_school
from src.drumsT_DIALOGS import add_newyear
from src.drumsT_FRAMES import lessons
from src.drumsT_DIALOGS import infoprg
from src.drumsT_SYS.os_filesystem import create_rootdir
from src.drumsT_SYS.SQLite_lib import School_Class

## COLORS:
azure = '#d9ffff' # rgb form (wx.Colour(217,255,255))
orange = '#ff5f1a' # rgb form (wx.Colour(255,95,26))
yellow = '#faff35'
red = '#ff3a1f'
greenolive = '#deffb4'
greenlight = '#91ff8f'
greendeph = '#516c1a'

class MainFrame(wx.Frame):
    """
    This is a main window of the selections and the 
    databases importing. 
    """
    def __init__(self):
        """
        Here set the attributes that pass at others dialogs and frame
        """
        #################### set attributes:
        self.drumsT_ico = wx.GetApp().drumsT_icon
        self.addStudent_ico = wx.GetApp().addStudent_icon
        self.openStudent_ico = wx.GetApp().openStudent_icon
        self.delStudent_ico = wx.GetApp().delStudent_icon
        self.changeStudent_ico = wx.GetApp().changeStudent_icon
        ####
        self.rootdir = wx.GetApp().rootdir # base diractory to save any db
        self.path_db = None # path name of current file .drtDB
        self.IDyear = None # db school year id
        self.schoolName = None # name of school
        self.IDprofile = None # identifier (IDclass integear) 
        self.name = None # name of a student
        self.surname = None # surname of a student
        self.phone = None
        self.address = None
        self.birthDate = None
        self.joinDate = None
        self.level = None
        
        ####################
        wx.Frame.__init__(self, None, -1, style=wx.DEFAULT_FRAME_STYLE)
        
        self.InitUI()
        
    def InitUI(self):
        """
        start with widgets and setup
        """
        panel = wx.Panel(self, wx.ID_ANY)
        self.tool_bar()
        self.menu_bar()
        self.sb = self.CreateStatusBar(1)
        import_btn = wx.Button(panel, wx.ID_ANY, (_("Import")))
        self.cmbx_year = wx.ComboBox(panel,wx.ID_ANY, 
                                     choices=['?? ?? ??'],
                                     style=wx.CB_DROPDOWN | wx.CB_READONLY
                                     )
        self.import_txt = wx.TextCtrl(panel, wx.ID_ANY, "", 
                                      style=wx.TE_READONLY | wx.TE_CENTRE
                                      )
        self.list_ctrl = wx.ListCtrl(panel, wx.ID_ANY, style=wx.LC_REPORT | 
                                     wx.SUNKEN_BORDER
                                     )
        #################### Properties
        self.SetTitle(_("DrumsT - School Management For Drum Teachers"))
        icon = wx.Icon()
        icon.CopyFromBitmap(wx.Bitmap(self.drumsT_ico, wx.BITMAP_TYPE_ANY))
        self.SetIcon(icon)
        self.SetSize((1250, 800))
        #import_btn.SetMinSize((180, -1))
        #import_btn.SetBackgroundColour(greenlight)
        self.cmbx_year.SetSelection(0)
        self.cmbx_year.Disable()
        self.import_txt.SetMinSize((270, -1))
        self.cmbx_year.SetMinSize((200, -1))
        self.import_txt.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL,
                                        wx.BOLD, 0, ""))
        #self.import_txt.SetForegroundColour(greendeph)
        self.import_txt.Disable()
        self.list_ctrl.SetToolTip(_("Double click or type enter or push "
                                  "'Open lesson in selection' to open "
                                  "a individual profile displayed in list"))
        
        self.list_ctrl.InsertColumn(0, 'ID', width=30)
        self.list_ctrl.InsertColumn(1, _('School Year'), width=100)
        self.list_ctrl.InsertColumn(2, _('Name'), width=120)
        self.list_ctrl.InsertColumn(3, _('Surname'), width=120)
        self.list_ctrl.InsertColumn(4, _('Phone'), width=140)
        self.list_ctrl.InsertColumn(5, _('Address'), width=300)
        self.list_ctrl.InsertColumn(6, _('Birth Date'), width=150)
        self.list_ctrl.InsertColumn(7, _('Joined Date'), width=150)
        self.list_ctrl.InsertColumn(8, _('Level-Course'), width=400)
        
        self.toolbar.EnableTool(wx.ID_FILE2, False)
        self.toolbar.EnableTool(wx.ID_FILE3, False)
        self.toolbar.EnableTool(wx.ID_FILE4, False)
        self.toolbar.EnableTool(wx.ID_FILE5, False)
        self.addate.Enable(False)
        
        ####################  Set layout

        siz_base = wx.FlexGridSizer(2,1,0,0)
        grd_s1 = wx.FlexGridSizer(1,3,0,40)
        #box_school.Lower()
        box_school = wx.StaticBox(panel, wx.ID_ANY, 
                                  _("School Database Importing:"))
        school = wx.StaticBoxSizer(box_school, wx.VERTICAL)
        school.Add(import_btn, wx.EXPAND,0)
        
        box_txt = wx.StaticBox(panel, wx.ID_ANY, _("Database Name Imported:"))
        dbname = wx.StaticBoxSizer(box_txt, wx.VERTICAL)
        dbname.Add(self.import_txt, wx.EXPAND,0)
        
        box_year = wx.StaticBox(panel, wx.ID_ANY, _("School Year selection:"))
        year = wx.StaticBoxSizer(box_year, wx.VERTICAL)
        year.Add(self.cmbx_year, wx.EXPAND,0)

        grd_s1.AddMany([(school),(dbname),(year)])
        
        siz_base.Add(grd_s1, 0, wx.ALL, 15)
        siz_base.Add(self.list_ctrl, 0, wx.ALL | wx.EXPAND, 15)

        panel.SetSizer(siz_base)
        siz_base.Fit(panel) 
        siz_base.AddGrowableCol(0)
        siz_base.AddGrowableRow(1)
        self.Layout()
        self.Centre()
        ######################## binding #####################
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.on_select, self.list_ctrl)
        self.Bind( wx.EVT_LIST_ITEM_DESELECTED, self.on_deselect, self.list_ctrl)
        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_enter, self.list_ctrl)
        self.Bind(wx.EVT_BUTTON, self.open_school, import_btn)
        self.cmbx_year.Bind(wx.EVT_COMBOBOX, self.on_year)
        self.Bind(wx.EVT_CLOSE, self.Exit)
        
        self.statusbar_msg(_("To use DrumsT, you must import a database "
                             "or create new schools location"), yellow)
    #-------------------------------------------------------#
    def statusbar_msg(self, msg, color):
        """
        set the status-bar with messages and color types
        """
        if color == None:
            self.sb.SetBackgroundColour(wx.NullColour)
        else:
            self.sb.SetBackgroundColour(color)
            
        self.sb.SetStatusText(msg)
        self.sb.Refresh()
    #-------------------------------------------------------#
    def set_listctrl(self):
        """
        Populate the list_ctrl with data or new data. Before to use this
        method first must be use self.list_ctrl.DeleteAllItems() method 
        otherwise append result upon in the list_ctrl
        """
        profiles = School_Class().displayclass(self.path_db, self.IDyear)
        if profiles == []:
            msg = (_("Empty database: There isn't any list to load. "
                     "You must add new students now"))
            self.statusbar_msg(msg, yellow)
            self.toolbar.EnableTool(wx.ID_FILE2, False)
            self.toolbar.EnableTool(wx.ID_FILE4, False)
            self.toolbar.EnableTool(wx.ID_FILE5, False)
            return

        index = 0
        for rec in profiles:
            rows = self.list_ctrl.InsertItem(index, str(rec[0]))
            self.list_ctrl.SetItem(rows, 0, str(rec[0]))
            self.list_ctrl.SetItem(rows, 1, rec[1])
            self.list_ctrl.SetItem(rows, 2, rec[2])
            self.list_ctrl.SetItem(rows, 3, rec[3])
            self.list_ctrl.SetItem(rows, 4, rec[4])
            self.list_ctrl.SetItem(rows, 5, rec[5])
            self.list_ctrl.SetItem(rows, 6, rec[6])
            self.list_ctrl.SetItem(rows, 7, rec[7])
            self.list_ctrl.SetItem(rows, 8, rec[8])
            if index % 2:
                self.list_ctrl.SetItemBackgroundColour(index, "white")
            else:
                 self.list_ctrl.SetItemBackgroundColour(index, greenolive)
            index += 1
            
    ########################### START WITH EVENTS HANDLER
    #------------------------------------------------------------------#
    def on_select(self, event): # list_ctrl
        """
        Event emitted when selecting item only.
        """
        index = self.list_ctrl.GetFocusedItem()
        item_ID = self.list_ctrl.GetItem(index,0)
        item_name = self.list_ctrl.GetItem(index,2)
        item_surname = self.list_ctrl.GetItem(index,3)
        item_phone = self.list_ctrl.GetItem(index,4)
        item_addr = self.list_ctrl.GetItem(index,5)
        item_birth = self.list_ctrl.GetItem(index,6)
        item_join = self.list_ctrl.GetItem(index,7)
        item_lev = self.list_ctrl.GetItem(index,8)
        
        self.IDprofile = item_ID.GetText()
        self.name = "%s" % (item_name.GetText())
        self.surname = "%s" % (item_surname.GetText())
        self.phone = "%s" % (item_phone.GetText())
        self.address = "%s" % (item_addr.GetText())
        self.birthDate = "%s" % (item_birth.GetText())
        self.joinDate = "%s" % (item_join.GetText())
        self.level = "%s" % (item_lev.GetText())
        
        self.toolbar.EnableTool(wx.ID_FILE2, True)
        self.toolbar.EnableTool(wx.ID_FILE4, True)
        self.toolbar.EnableTool(wx.ID_FILE5, True)
    #-------------------------------------------------------------------#
    def on_deselect(self, event): # list_ctrl
        """
        Event emitted when de-selecting all item
        """
        self.toolbar.EnableTool(wx.ID_FILE2, False)
        self.toolbar.EnableTool(wx.ID_FILE4, False)
        self.toolbar.EnableTool(wx.ID_FILE5, False)
        
        self.IDprofile = None # identifier (IDclass integear) 
        self.name = None # name of a student
        self.surname = None # surname of a student
        self.phone = None
        self.address = None
        self.birthDate = None
        self.joinDate = None
        self.level = None
    #-------------------------------------------------------------------#
    def on_enter(self, event): # list_ctrl
        """
        If type enter key or double clicked mouse, the event 
        open a Lesson
        """
        nameSur = "%s %s" % (self.name,self.surname)
        frame = lessons.Lesson(nameSur, 
                               self.IDprofile, 
                               self.path_db, 
                               parent=wx.GetTopLevelParent(self),
                               )
        frame.Show()
        #schools = School_Class().displaystudent(self.IDprofile ,self.path_db)
    #-------------------------------------------------------------------#
    def open_school(self, event): # import button
        """
        Open a existing database with .drtDB extension. The filedialog 
        is set to opening in the 'drumsT_DB' directory 
        """
        wildcard = ("drumsT db (*.drtDB)|*.drtDB|" "All files (*.*)|*.*")
        dialfile = wx.FileDialog(self, 
                       _("Select filename with '.drtDB' extension "),
                       ".", "", wildcard, wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        dialfile.SetDirectory(self.rootdir)
        
        if dialfile.ShowModal() == wx.ID_OK: 
            self.schoolName = dialfile.GetFilename().split(".drtDB")[0]
            self.path_db = dialfile.GetPath()
            self.cmbx_year.Enable(), self.cmbx_year.Clear()
            self.cmbx_year.Append('?? ?? ??')
            year = School_Class().displayschool(self.path_db)

            for items in year:
                self.cmbx_year.Append(items[0])# can be more data
                
            self.cmbx_year.SetSelection(0)
            self.import_txt.Enable(), self.import_txt.SetValue("")
            self.import_txt.AppendText(dialfile.GetFilename())
            
            if self.list_ctrl.GetItemCount() > 0:# if list_ctrl is not empty
                self.list_ctrl.DeleteAllItems()
                self.toolbar.EnableTool(wx.ID_FILE2, False)
                self.toolbar.EnableTool(wx.ID_FILE3, False)
                self.toolbar.EnableTool(wx.ID_FILE4, False)
                self.toolbar.EnableTool(wx.ID_FILE5, False)
            self.statusbar_msg('', None)
            self.addate.Enable(True)# enable add new year menu
    #-------------------------------------------------------------------#
    def on_year(self, event): # combobox
        """
        When select a item in cmbx_year go in this setup
        """
        if self.cmbx_year.GetValue() == '?? ?? ??':
            self.list_ctrl.DeleteAllItems()
            self.toolbar.EnableTool(wx.ID_FILE2, False)
            self.toolbar.EnableTool(wx.ID_FILE3, False)
            self.toolbar.EnableTool(wx.ID_FILE4, False)
            self.toolbar.EnableTool(wx.ID_FILE5, False)
        else:
            #year = self.cmbx_year.GetValue()
            self.IDyear = self.cmbx_year.GetValue()
            self.toolbar.EnableTool(wx.ID_FILE3, True)
            self.list_ctrl.DeleteAllItems()
            self.set_listctrl()
    #-------------------------------------------------------------------#

    ######################################################################
    #------------------------Build the Tool Bar--------------------------#
    ######################################################################
    def tool_bar(self):
        """
        Makes and attaches the view tools bar
        """
        #--------- Properties
        self.toolbar = self.CreateToolBar(style=(wx.TB_HORZ_LAYOUT | 
                                                 wx.TB_TEXT))
        self.toolbar.SetToolBitmapSize((36,36))
        self.toolbar.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL,
                                     wx.NORMAL, 0, ""))

        # ------- See student data
        pupil = self.toolbar.AddTool(wx.ID_FILE2, 
                                     _('Open lessons register'),
                                     wx.Bitmap(self.openStudent_ico))
        self.toolbar.AddSeparator()
        
        # ------- Add new student
        addpupil = self.toolbar.AddTool(wx.ID_FILE3, 
                                        _('Add New Student'), 
                                        wx.Bitmap(self.addStudent_ico))
        self.toolbar.AddSeparator()
        
        # ------- Modify student data
        modifypupil = self.toolbar.AddTool(wx.ID_FILE4, 
                                           _('data change student'), 
                                           wx.Bitmap(self.changeStudent_ico))
        self.toolbar.AddSeparator()
        
        # ------- DSelete tudent
        deletepupil = self.toolbar.AddTool(wx.ID_FILE5, 
                                           _('data delete student'), 
                                           wx.Bitmap(self.delStudent_ico))
        self.toolbar.AddSeparator()
        
        # ----------- finally, create it
        self.toolbar.Realize()
        
        #------------ Binding
        self.Bind(wx.EVT_TOOL, self.Pupil, pupil)
        self.Bind(wx.EVT_TOOL, self.Addpupil, addpupil)
        self.Bind(wx.EVT_TOOL, self.Modify, modifypupil)
        self.Bind(wx.EVT_TOOL, self.Delete, deletepupil)
        
    #-------------------------EVENTS-----------------------------------#
    #------------------------------------------------------------------#

    def Pupil(self, event):
        """
        open a new Lesson and a Overall view program
        """
        self.on_enter(self)
    #------------------------------------------------------------------#
    def Addpupil(self, event):
        """
        Add one new record to Class table.
        Also, this method call a reset to 'None' 
        any previous setting attributes (see self.on_select) 
        and disable some buttons into toolbar:
        """
        dialog = add_student.AddRecords(self,
                                    _("Add new identity profile to database"),
                                    None,None,None,None,None,None,None
                                      )
        ret = dialog.ShowModal()
        
        if ret == wx.ID_OK:
            data = dialog.GetValue()
            check = School_Class().checkstudent(data[0],data[1],
                                                self.path_db, self.IDyear)
        else:
            return
            
        if check[0]:
            warn = wx.MessageDialog(self, check[1], 
                                    _("DrumsT: Warning"), 
                                    wx.YES_NO | 
                                    wx.CANCEL | 
                                    wx.ICON_EXCLAMATION
                                    )
            
            if warn.ShowModal() == wx.ID_YES:
                pass
            else:
                return
            
        add = School_Class().insertstudent(data, self.path_db, self.IDyear)
        if add[0]:
            wx.MessageBox(add[1], _('DrumsT: Error'), wx.ICON_ERROR, self)
            return
        
        wx.MessageBox(_("Successfull storing !"), 
                      _("Success"), 
                      wx.OK, 
                      self
                      )
        self.list_ctrl.DeleteAllItems() # clear all items in list_ctrl
        self.set_listctrl() # re-charging list_ctrl with newer
        self.statusbar_msg(_('It was added a new profile'), greenolive)
        self.on_deselect(self) # reset attributes and disable buttons 
        
    #------------------------------------------------------------------#
    def Modify(self, event):
        """
        change data identity of the selected item.
        If a name/surname already exist a raise message will 
        be display. Also, this method call a reset to 'None' 
        any previous setting attributes (see self.on_select) 
        and disable some buttons into toolbar:
        """
        dialog = add_student.AddRecords(self,
                            _("Change data into selected identity profile"),
                            self.name,
                            self.surname, 
                            self.phone, 
                            self.address,
                            self.birthDate,
                            self.joinDate,
                            self.level,
                                        )
        ret = dialog.ShowModal()
        if ret == wx.ID_OK:
            data = dialog.GetValue()
            check = School_Class().checkstudent(data[0],data[1],
                                                self.path_db, self.IDyear)
        else:
            return
            
        if check[0]:
            warn = wx.MessageDialog(self, check[1], 
                                    _("DrumsT: Warning"), 
                                    wx.YES_NO | 
                                    wx.CANCEL | 
                                    wx.ICON_EXCLAMATION)
            
            if warn.ShowModal() == wx.ID_YES:
                pass
            else:
                return
            
        change = School_Class().change_class_item(data, self.IDprofile,
                                                  self.path_db
                                                  )
        if change[0]:
            wx.MessageBox(change[1], _('DrumsT: Error'), wx.ICON_ERROR, self)
            return
        
        wx.MessageBox(_("Successfull storing !"), 
                      _("DrumsT: Success!"), 
                      wx.OK, 
                      self)

        self.list_ctrl.DeleteAllItems() # clear all items in list_ctrl
        self.set_listctrl() # re-charging list_ctrl with newer
        self.statusbar_msg(_('Update new profile'), greenolive)
        self.on_deselect(self) # reset attributes and disable buttons 
    #------------------------------------------------------------------#
    def Delete(self, event):
        """
        Cancel the selected item and all its information stored 
        into table db. Also, this method call a reset to 'None' 
        any previous setting attributes (see self.on_select) 
        and disable some buttons into toolbar:
        """
        msg = (_("Are you sure to delete selected student?\n\n"
               "Note that this process remove all stored\n"
               "information, included all stored lessons.\n\n"
               "After this action all the deleted data will\n"
               "not be recoverable !")
               )
        warn = wx.MessageDialog(self, msg, _("DrumsT: Warning"), wx.YES_NO | 
                                wx.CANCEL | wx.ICON_INFORMATION
                                )
        if warn.ShowModal() == wx.ID_YES:
            pass
        else:
            return
        
        cancel = School_Class().delete_profile(self.IDprofile, self.path_db)
        if cancel[0]:
            wx.MessageBox(cancel[1], _('DrumsT: Error'), wx.ICON_ERROR, self)
            return
        
        wx.MessageBox(_("{0} {1} with ID class {2} was deleted").format(
                        self.name,
                        self.surname, 
                        self.IDprofile), 
                        _("DrumsT: Success"), 
                        wx.OK, self
                      )
        self.list_ctrl.DeleteAllItems() # clear all items in list_ctrl
        self.set_listctrl() # re-charging list_ctrl with newer
        self.statusbar_msg(_("{0} {1} with ID class {2} was deleted").format(
                                                         self.name,
                                                         self.surname, 
                                                         self.IDprofile), 
                                                         yellow
                                                         )
        self.on_deselect(self) # reset attributes and disable buttons 

    ######################################################################
    #------------------------Build Menu Bar-----------------------------#
    ######################################################################
    def menu_bar(self):
        """
        Makes and attaches the view menu

        """
        menuBar = wx.MenuBar()
        
        #------------------- File
        fileMenu = wx.Menu()
        exitItem = fileMenu.Append(wx.ID_EXIT, _("&Quit"), 
                                   _("Exit the application"))
        menuBar.Append(fileMenu, _("&File"))

        #------------------- Tools
        schoolButton = wx.Menu()
        
        addschool = schoolButton.Append(wx.ID_ANY, _("Add new school"), 
                                        _("Create a new school location"))
        schoolButton.AppendSeparator()
        self.addate = schoolButton.Append(wx.ID_ANY, _("Add new school year"), 
                            _("Record a new school year to imported database"))
        
        menuBar.Append(schoolButton,_("&Schools"))

        #------------------ help buton
        helpButton = wx.Menu()
        helpItem = helpButton.Append( wx.ID_HELP, _("&Help"), 
                                                  _("Online help")
                                     )
        infoItem = helpButton.Append(wx.ID_ABOUT, _("&About.."), 
                                                  _("About the program")
                                    )
        menuBar.Append(helpButton,_("&Help"))
        
        # ...and set, finally .
        self.SetMenuBar(menuBar)

        #-----------------------Binding menu bar-------------------------#
        # menu tools
        self.Bind(wx.EVT_MENU, self.Addschool, addschool)
        self.Bind(wx.EVT_MENU, self.Addate, self.addate)
        self.Bind(wx.EVT_MENU, self.Exit, exitItem)
        #----HELP----
        #self.Bind(wx.EVT_MENU, self.Helpme, helpItem)
        self.Bind(wx.EVT_MENU, self.Info, infoItem)

        
    #-----------------Callback menu bar (event handler)------------------#
    #------------------------------------------------------------------#
    def Addschool(self, event):
        """
        Add new school with a school year. This method make a new 
        directory with school name and insert data to database.
        """

        dialog = add_school.AddSchool(self,
                                      _("DrumsT - Add new school and date")
                                      )
        retcode = dialog.ShowModal()

        if retcode == wx.ID_OK:
            data = dialog.GetValue()
        else:
            return
        
        mkdirs = create_rootdir(self.rootdir,data[0])
        if mkdirs[0]:
            wx.MessageBox(mkdirs[1], 'DrumsT: Error', wx.ICON_ERROR, self)
            return
        schools = School_Class().newSchoolyear(self.rootdir,data[0],data[1])
        if schools[0]:
            wx.MessageBox(schools[1], 'DrumsT: Error', wx.ICON_ERROR, self)
            return
        
        wx.MessageBox(_('DrumsT: Success on create new school'), 'Info',
                      wx.ICON_INFORMATION, self)
    #------------------------------------------------------------------#
    def Addate(self, event):
        """
        Add new date event into selected school.
        """
        dialog = add_newyear.AddYear(self, "DrumsT")
        retcode = dialog.ShowModal()
        
        if retcode == wx.ID_OK:
            data = dialog.GetValue()
        else:
            return
        
        schools = School_Class().updateyear(self.path_db, data)
        if schools[0]:
            wx.MessageBox(schools[1], 
                          _('DrumsT: Error'), 
                          wx.ICON_ERROR, self
                          )
            return
        
        wx.MessageBox(_('DrumsT: Success on create new year'), 
                        'Info', 
                        wx.ICON_INFORMATION, 
                        self
                      )
        self.cmbx_year.Append(data)
        
        
    def Exit(self, event):
        print ('exit')
        self.Destroy()
        
        
    #------------------------------------------------------------------#
    def Info(self, event):
        """
        Display the program informations and developpers
        """
        infoprg.info(self.drumsT_ico)

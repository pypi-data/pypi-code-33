#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#########################################################
# Name: first_time_start.py
# Porpose: Showing when there is not nothing database
# Compatibility: Python3
# Platform: all
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2017-2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Created: 1 Feb. 2019
# Rev (00),(01)

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
from src.drumsT_DIALOGS.add_school import AddSchool
from src.drumsT_SYS.SQLite_lib import School_Class
from src.drumsT_SYS.os_filesystem import write_newpath
from src.drumsT_SYS.os_filesystem import create_rootdir

#from src.drumsT_SYS.SQLite_lib import School_Class
#from src.drumsT_SYS.boot import write_fileconf
class FirstStart(wx.Dialog):
    
    def __init__(self, img):

        wx.Dialog.__init__(self, None, -1, style=wx.DEFAULT_DIALOG_STYLE)
        
        # variables or attributes:
        msg = (_("This is the first time you start DrumsT.\n\n"
               "DrumsT uses only one path to save databases.\n\n"
               "- To create a new database now, press the "
               "create button.\n- If a database already exists press "
               "the import button.\n- Press the exit button to exit simply"))
        
        # widget:
        bitmap_drumsT = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(
            img,wx.BITMAP_TYPE_ANY))
        lab_welc2 = wx.StaticText(self, wx.ID_ANY, (msg))
        lab_welc1 = wx.StaticText(self, wx.ID_ANY, (_("Welcome !")))
        lab_create = wx.StaticText(self, wx.ID_ANY, 
                                   (_("Create a new database:")))
        lab_import = wx.StaticText(self, wx.ID_ANY, (
                                _("Import a 'drumsT_DB' existing folder:")))
        lab_exit = wx.StaticText(self, wx.ID_ANY, 
                                 (_("Exit and do nothing:")))
        create_btn = wx.Button(self, wx.ID_ANY, (_("Create")))
        import_btn = wx.Button(self, wx.ID_ANY, (_("Import")))
        close_btn = wx.Button(self, wx.ID_EXIT, "&Quit")
        
        # properties
        self.SetTitle("DrumsT")
        lab_welc1.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL,wx.BOLD, 0, ""))
        # layout:
        grd_base = wx.GridSizer(2, 1, 0, 0)
        grd_1 = wx.FlexGridSizer(1, 2, 0, 0)
        grd_ext = wx.FlexGridSizer(2, 1, 0, 0)
        grd_2 = wx.FlexGridSizer(3, 2, 0, 0)
        grd_base.Add(grd_1)
        grd_1.Add(bitmap_drumsT,0,wx.ALL, 15)
        grd_1.Add(grd_ext)
        grd_base.Add(grd_2)
        grd_ext.Add(lab_welc1,0,  wx.ALL, 15)
        grd_ext.Add(lab_welc2,0, wx.ALIGN_CENTER | wx.ALL, 15)
        grd_2.Add(lab_create,0, wx.ALIGN_CENTER | wx.ALL, 15)
        grd_2.Add(create_btn,0, wx.ALIGN_CENTER | wx.ALL, 15)
        grd_2.Add(lab_import,0, wx.ALIGN_CENTER | wx.ALL, 15)
        grd_2.Add(import_btn,0, wx.ALIGN_CENTER | wx.ALL, 15)
        grd_2.Add(lab_exit,0, wx.ALIGN_CENTER | wx.ALL, 15)
        grd_2.Add(close_btn,0, wx.ALIGN_CENTER | wx.ALL, 15)
        self.SetSizer(grd_base)
        grd_base.Fit(self)
        self.Layout()
        
        ######################## bindings #####################
        self.Bind(wx.EVT_BUTTON, self.on_close)
        self.Bind(wx.EVT_BUTTON, self.create_now, create_btn)
        self.Bind(wx.EVT_BUTTON, self.import_now, import_btn)
        
    # EVENTS:
    #-------------------------------------------------------------------#
    def on_close(self, event):
        self.Destroy()
    #-------------------------------------------------------------------#
    def create_now(self, event):
        """
        Create new 
        """
        dialog = AddSchool(self, _("DrumsT - create new school database"))
        retcode = dialog.ShowModal()

        if retcode == wx.ID_OK:
            data = dialog.GetValue()
        else:
            wx.MessageBox(_("You could not set anything"), 
                          _('DrumsT: Warning'), wx.ICON_EXCLAMATION, self)
            return
        
        dialogdir = wx.DirDialog(self, _("Where do you want to save ?"))
        
        if dialogdir.ShowModal() == wx.ID_OK:
            path = '%s/drumsT_DB' % dialogdir.GetPath()
            dialogdir.Destroy()
            
            mkdirs = create_rootdir(path,data[0])
            if mkdirs[0]:
                wx.MessageBox(mkdirs[1], 
                              _('DrumsT: Error'), 
                              wx.ICON_ERROR, 
                              self
                              )
                return

            schools = School_Class().newSchoolyear(path,data[0],data[1])
            if schools[0]:
                wx.MessageBox(schools[1], 
                              _('DrumsT: Error'), 
                              wx.ICON_ERROR, 
                              self
                              )
                return

            setPath = write_newpath(path) # writing drumsT.conf
            if setPath[0]:
                wx.MessageBox(setPath[1], 
                              _('DrumsT: Error'), 
                              wx.ICON_ERROR, 
                              self
                              )
                return
            else:
                wx.MessageBox(_("A new drumsT rootdir has been created:"
                              "\n\n{0}\n\nYou must re-start the DrumsT "
                              "application now.\n\nGood Work !").format(path), 
                              _('Success !'), wx.ICON_INFORMATION, self)
                self.Destroy()
        else:
            wx.MessageBox(_("You could not set anything"), 
                          _('DrumsT: Warning'), 
                          wx.ICON_EXCLAMATION, 
                          self
                          )
            return
    #-------------------------------------------------------------------#
    def import_now(self, event):
        """
        Import one directory with saved db
        """
        dialdir = wx.DirDialog(self, _("Where is the 'DrumsT_DB' folder?"))
        if dialdir.ShowModal() == wx.ID_OK:
            path = dialdir.GetPath()
            dialdir.Destroy()
            
            setPath = write_newpath(path) # writing drumsT.conf
            if setPath[0]:
                wx.MessageBox(setPath[1], 
                              _('DrumsT: Error'), 
                              wx.ICON_ERROR, 
                              self
                              )
                return
            else:
                wx.MessageBox(_("A database has been imported successfully:"
                              "\n\n{0}\n\nYou must re-start the DrumsT "
                              "application now.\n\nGood Work !").format(path), 
                              _('Success !'), wx.ICON_INFORMATION, self)
                self.Destroy()
        else:
            wx.MessageBox(_("You could not set anything"), 
                          _('DrumsT: Warning'), wx.ICON_EXCLAMATION, self)
            return

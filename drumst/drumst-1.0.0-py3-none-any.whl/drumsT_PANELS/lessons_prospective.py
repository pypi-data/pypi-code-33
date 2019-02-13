#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#########################################################
# Name: lesson_prospective.py
# Porpose: Show data of all lessons of a one student
# Compatibility: Python3
# Platform: all
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2017-2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
# license: GPL3
# Created: 1 Feb. 2019
# Rev (00)

# This file is part of DrumsT.

# DrumsT is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# DrumsT is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with DrumsT. If not, see <http://www.gnu.org/licenses/>.
#########################################################

import wx
import wx.grid as  gridlib
from drumsT.drumsT_SYS.SQLite_lib import School_Class

class PanelTwo(wx.Panel):
    """
    Show a grid with tabular data.
    
    It was inspired on codes from:
    <http://www.blog.pythonlibrary.org/2013/10/31/wxpython-how-to-get-
    selected-cells-in-a-grid/>
    <http://www.blog.pythonlibrary.org/2010/04/04/wxpython-grid-tips-and-
    tricks/>
    <http://www.blog.pythonlibrary.org/2010/03/18/wxpython-an-
    introduction-to-grids/>
    
    Official Documents:
    <http://wxpython.org/Phoenix/docs/html/grid.Grid.html>
    """
    def __init__(self, parent, nameSur, IDclass, path_db):
        """
        Display a list with data of all previous lessons of
        the student in object and relating to school
        year selected only 
        """
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)
        #### set attributes:
        self.currentlySelectedCell = (0, 0) # row, col default
        self.rowEdit = None # tracking what row is was edited
        self.newsEdit = [] # list of all item edited
        self.backUp = [] # last backup for recovery
        self.index = 0 # how many items (rows) 
        self.path_db = path_db
        self.IDclass = IDclass
        self.IDlesson = None
        self.parent = parent
        
        self.InitUI()
        
    def InitUI(self):
        """
        Start with widget and panel setup
        """
        self.editBtn = wx.Button(self, wx.ID_ANY, (_("Edit Topic")))
        self.rollbackBtn = wx.Button(self, wx.ID_UNDO, (_("&Undo")))
        #self.applyBtn = wx.Button(self, wx.ID_ANY, (_("Apply Changes")))
        self.myGrid = gridlib.Grid(self)
        #### properties:
        self.myGrid.EnableEditing(False) # make all in read only
        self.myGrid.CreateGrid(150, 15)
        self.myGrid.SetColLabelValue(0, _("ID lesson"))
        self.myGrid.SetColLabelValue(1, _("ID class"))
        self.myGrid.SetColLabelValue(2, _("Attendances"))
        self.myGrid.SetColLabelValue(3, _("Lesson Date"))
        self.myGrid.SetColLabelValue(4, _("Chart Reading"))
        self.myGrid.SetColLabelValue(5, _("Hands/foots Setting"))
        self.myGrid.SetColLabelValue(6, _("Rudiments"))
        self.myGrid.SetColLabelValue(7, _("Coordination"))
        self.myGrid.SetColLabelValue(8, _("Styles"))
        self.myGrid.SetColLabelValue(9, _("Minus One"))
        self.myGrid.SetColLabelValue(10, _("Other-1"))
        self.myGrid.SetColLabelValue(11, _("Other-2"))
        self.myGrid.SetColLabelValue(12, _("Other-3"))
        self.myGrid.SetColLabelValue(13, _("Votes"))
        self.myGrid.SetColLabelValue(14, _("Note/Reminder"))
        btnExit = wx.Button(self, wx.ID_CANCEL, ("&Cancel"))
        self.applyBtn = wx.Button(self, wx.ID_APPLY, ("&Apply"))
        #### set columns 0-1-2 in read only
        # see above address: www.../wxpython-an-introduction-to-grids/
        #attr = gridlib.GridCellAttr()
        #attr.SetReadOnly(True)
        #self.myGrid.SetColAttr(0, attr)
        #self.myGrid.SetColAttr(1, attr)
        #self.myGrid.SetColAttr(2, attr)
        ## oppure: self.myGrid.SetReadOnly(3, 3, True)
        #### properties
        self.editBtn.SetToolTip(_("Edit text or values into the "
                                     "cells and append"))
        self.rollbackBtn.SetToolTip(_("Restore to the previous state"))
        self.applyBtn.SetToolTip(_("Update and commit new entries "
                                   "into database"))
        self.editBtn.Disable()
        self.rollbackBtn.Disable()
        self.applyBtn.Disable()
        #### go to popular the grid:
        self.setting()
        #### Build Layout:
        sizer = wx.BoxSizer(wx.VERTICAL)
        gridSiz = wx.GridSizer(1,2,0,0)
        sizer.Add(gridSiz, 0, wx.ALL, 5)
        gridSiz.Add(self.editBtn, 0, wx.ALL, 5)
        gridSiz.Add(self.rollbackBtn, 0, wx.ALL, 5)
        sizer.Add(self.myGrid, 1, wx.EXPAND, 5)
        gridBottom = wx.GridSizer(1,2,0,0)
        gridBottom.Add(btnExit, 0, wx.ALL, 5)
        gridBottom.Add(self.applyBtn, 0, wx.ALL, 5)
        sizer.Add(gridBottom, flag=wx.ALL|wx.ALIGN_RIGHT|wx.RIGHT, border=5)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
        #### binding
        self.myGrid.Bind(gridlib.EVT_GRID_SELECT_CELL, self.onSingleSelect)
        self.Bind(wx.EVT_BUTTON, self.editCells, self.editBtn)
        self.Bind(wx.EVT_BUTTON, self.restroreLast, self.rollbackBtn)
        self.Bind(wx.EVT_BUTTON, self.makeChange, self.applyBtn)
        btnExit.Bind(wx.EVT_BUTTON, self.on_close)
    #-------------------------
    def setting(self):
        """
        Set properties and set the grid cells with values
        of the query.
        """
        lessons = School_Class().showInTable(self.IDclass, self.path_db)
        for n, item in enumerate(lessons):
            self.index += 1
            #------------IDlesson
            self.myGrid.SetCellValue(n , 0, str(item[0]))
            self.myGrid.SetCellAlignment(n, 
                                         0, 
                                         wx.ALIGN_CENTRE, 
                                         wx.ALIGN_CENTRE
                                         )
            #------------IDclass
            self.myGrid.SetCellValue(n , 1, str(item[1])) # IDclass
            self.myGrid.SetCellAlignment(n, 
                                         1, 
                                         wx.ALIGN_CENTRE, 
                                         wx.ALIGN_CENTRE
                                         )
            #------------attendances
            self.myGrid.SetCellValue(n , 2, item[2])
            if item[2] == _('No absence'):
                self.myGrid.SetCellTextColour(n, 2, '#516c1a')
            elif item[2] == _('Student is absent'):
                self.myGrid.SetCellTextColour(n, 2, wx.RED)
            elif item[2] == _('Teacher is absent'):
                self.myGrid.SetCellTextColour(n, 2, '#e1cf37')
            self.myGrid.SetCellFont(n, 2, wx.Font(10, 
                                                  wx.DEFAULT, 
                                                  wx.NORMAL, 
                                                  wx.BOLD))
            self.myGrid.SetCellAlignment(n, 
                                         2, 
                                         wx.ALIGN_CENTRE, 
                                         wx.ALIGN_CENTRE
                                         )
            #-----------date
            self.myGrid.SetCellValue(n , 3, item[3])# date
            self.myGrid.SetCellBackgroundColour(n, 3, '#deffb4')
            #-----------
            if item[4] == 'NONE':
                self.myGrid.SetCellValue(n, 4, '')
            else:
                self.myGrid.SetCellValue(n , 4, item[4]) # reading
            
            if item[5] == 'NONE':
                self.myGrid.SetCellValue(n, 5, '')
            else:
                self.myGrid.SetCellValue(n , 5, item[5]) # setting
                
            if item[6] == 'NONE':
                self.myGrid.SetCellValue(n, 6, '')
            else:
                self.myGrid.SetCellValue(n , 6, item[6]) # rudiments
                
            if item[7] == 'NONE':
                self.myGrid.SetCellValue(n, 7, '')
            else:
                self.myGrid.SetCellValue(n , 7, item[7]) # coordination
                
            if item[8] == 'NONE':
                self.myGrid.SetCellValue(n, 8, '')
            else:
                self.myGrid.SetCellValue(n , 8, item[8]) # styles
                
            if item[9] == 'NONE':
                self.myGrid.SetCellValue(n, 9, '')
            else:
                self.myGrid.SetCellValue(n , 9, item[9]) # minusone
                
            if item[10] == 'NONE':
                self.myGrid.SetCellValue(n, 10, '')
            else:
                self.myGrid.SetCellValue(n , 10, item[10]) # other1
                
            if item[11] == 'NONE':
                self.myGrid.SetCellValue(n, 11, '')
            else:
                self.myGrid.SetCellValue(n , 11, item[11]) # other2
                
            self.myGrid.SetCellValue(n , 12, item[12]) # other3
            if item[12] == 'NONE':
                self.myGrid.SetCellValue(n, 12, '')
                
            if item[13] == 'NONE':
                self.myGrid.SetCellValue(n, 13, '')
            else:
                self.myGrid.SetCellValue(n , 13, item[13]) # votes
                
            if item[14] == 'NONE':
                self.myGrid.SetCellValue(n , 14, '')
            else:
                self.myGrid.SetCellValue(n , 14, item[14]) # notes
            self.myGrid.SetCellBackgroundColour(n, 14, '#fffa9a')
            
        self.myGrid.AutoSizeColumns(setAsMin=True) # resize all columns
        self.myGrid.AutoSizeRows(setAsMin=True) # resize all rows
    #--------------------------------------------------------------------#
    #--------------------------------EVENT-------------------------------#
    def editCells(self, event):
        """
        Make editable the columns in the row where the 
        cell is only selected
        """
        row = self.currentlySelectedCell[0]
        col = self.currentlySelectedCell[1]
        val = self.myGrid.GetCellValue(row,col)
        topicname = self.myGrid.GetColLabelValue(col)
        topicnumber = self.myGrid.GetRowLabelValue(row)
        
        
        if self.rowEdit is None or self.rowEdit == row:
            if col == 0 or col == 1:
                wx.MessageBox(_("This column can not be edit."), 
                _('DrumsT'), wx.ICON_INFORMATION, self)
                return
            
            if self.IDlesson not in self.backUp:
                del self.backUp[:] # first clear list
                for n in range(15):
                    i = self.myGrid.GetCellValue(row, n)
                    self.backUp.append(i)
            
            if col == 2:
                choices = [_("No absence"),
                           _("Student is absent"),
                           _("Teacher is absent"),
                           ]
                mess = _("Edit the '{0}' topic in the "
                       "{1}th lesson      ").format(topicname, 
                                                   topicnumber
                                                   )
                choiceDlg = wx.SingleChoiceDialog(self, 
                                                 (mess), 
                                                 "DumsT: Change Attendances",
                                                 choices
                                                 )
                choiceDlg.SetClientSize(wx.Size(350, 250))
                if choiceDlg.ShowModal() == wx.ID_OK:
                    ret = choiceDlg.GetStringSelection()
                    choiceDlg.Destroy()
                else:
                    choiceDlg.Destroy()
                    return
            else:
                mess = _("Edit the '{0}' topic in the "
                       "{1}th lesson      ").format(topicname, 
                                                   topicnumber
                                                   )
                entriesDlg = wx.TextEntryDialog(self,
                                               (mess),
                                               ("DrumsT: Edit topic"),
                                               val,
                                               style=wx.TE_MULTILINE|
                                               wx.OK|
                                               wx.CANCEL
                                               )
                entriesDlg.SetClientSize(wx.Size(500, 300))
                if entriesDlg.ShowModal() == wx.ID_OK:
                    ret = entriesDlg.GetValue()
                    entriesDlg.Destroy()
                else:
                    entriesDlg.Destroy()
                    return
                    
            self.myGrid.SetCellValue(row , col, ret)
            
            del self.newsEdit[:] # first clear list 
            for n in range(15):
                i = self.myGrid.GetCellValue(row, n)
                self.newsEdit.append(i)
                
            self.rowEdit = row
            self.rollbackBtn.Enable()
            self.applyBtn.Enable()
        else:
            msg = (_("Before editing cells in other rows, you need to \n"
                     "render the changes with the 'Apply' button."))
            self.myGrid.SelectRow(self.rowEdit, addToSelected=True)
            wx.MessageBox(msg,
                          _('DrumsT: Change Not Allowed'), 
                          wx.ICON_INFORMATION, 
                          self
                          )
    #----------------------------------------------------------------------
    def restroreLast(self, event):
        """
        Retrieve last change and reset attributes. The data 
        retrieving of previous setting it is restored. 
        WARNING: this not restore after a apply-commit
        """
        for n, item in enumerate(self.backUp):
            self.myGrid.SetCellValue(self.rowEdit , n, self.backUp[n])
        self.editBtn.Disable()
        self.rollbackBtn.Disable()
        self.applyBtn.Disable()
        self.rowEdit = None
        del self.newsEdit[:]
        del self.backUp[:]
        self.IDlesson = None
    #----------------------------------------------------------------------
    def makeChange(self, event):
        """
        Allow to save changes in db (table Lesson) 
        """
        for n, item in enumerate(self.newsEdit):
            # if empty str fill out with NONE str
            if item.strip() == '':
                self.newsEdit[n] = 'NONE'
                
        change = School_Class().change_lesson_items(self.newsEdit, 
                                                    self.path_db
                                                    )
        if change[0]:
            wx.MessageBox(change[1], _('DrumsT: Error'), wx.ICON_ERROR, self)
            return
        
        self.editBtn.Disable()
        self.rollbackBtn.Disable()
        self.applyBtn.Disable()
        self.rowEdit = None
        del self.newsEdit[:]
        del self.backUp[:]
        self.IDlesson = None
        
        self.index = 0 
        self.setting()
        wx.MessageBox(_("DrumsT: Successfully stored!"), 
                      _("Info"), 
                      wx.OK, 
                      self)
        #----------------------------------------------------------------------
    def onSingleSelect(self, event):
        """
        Get the selection of a single cell by clicking or 
        moving the selection with the arrow keys
        """
        self.currentlySelectedCell = (event.GetRow(),
                                    event.GetCol())
        self.IDlesson = self.myGrid.GetCellValue(self.currentlySelectedCell[0], 
                                                 0)
        if event.GetRow() >= self.index:
            self.editBtn.Disable()
            return
        else:
            self.editBtn.Enable()
        event.Skip()
    #----------------------------------------------------------------------
    def on_close(self, event):
        #self.parent.Destroy()
        self.parent.on_close(self)
        #event.Skip()
    #-----------------------------------------------------------------------#
    

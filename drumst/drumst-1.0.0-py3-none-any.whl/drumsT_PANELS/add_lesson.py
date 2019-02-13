#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#########################################################
# Name: add_lesson.py
# Porpose: Add a new lesson recording
# Compatibility: Python3
# Platform: all
# Writer: Gianluca Pernigoto <jeanlucperni@gmail.com>
# Copyright: (c) 2015-2019 Gianluca Pernigoto <jeanlucperni@gmail.com>
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

import wx
import wx.adv
from drumsT.drumsT_SYS.SQLite_lib import School_Class

class PanelOne(wx.Panel):
    """
    Shows the interface for data entry on the current lesson. 
    When make a new day lesson is more comfortable to use this 
    panel than using a grid (i think)
    """
    def __init__(self, parent, nameSur, IDclass, path_db):
        """
        NOTE: 
        you can only record a lesson time. when you save a lesson, 
        to record a next sequence it is necessary to close 
        this window, that is its parent (frame)
        """
        wx.Panel.__init__(self, parent, -1, style=wx.TAB_TRAVERSAL)
        self.currdate = None # current date
        self.switch = False # switch for check absences
        self.nameSur = nameSur # name/surname of student
        self.IDclass = IDclass # Id of Class table
        self.path_db = path_db # database filename
        self.parent = parent 
        
        self.InitUI()

    def InitUI(self):
        """
        Start with widget and panel setup
        """
        self.enableLesson = wx.ToggleButton(self, wx.ID_ANY, 
                                            _("Start New Lesson"))
        self.datepk = wx.adv.DatePickerCtrl(self, wx.ID_ANY, 
                                            style=wx.adv.DP_DEFAULT
                                            )
        self.boxDate = wx.StaticBox(self, wx.ID_ANY, (_("lesson date setting")))
        self.rdb = wx.RadioBox(self, 
                               wx.ID_ANY, (_("Attendances Register")), 
                               choices=[(_("No absence")),
                                        (_("Student is absent")),
                                        (_("Teacher is absent")),
                                        ],
                               majorDimension=0,style=wx.RA_SPECIFY_COLS
                               )
        notebook = wx.Notebook(self, wx.ID_ANY)
        #### insert widget in first notebook table
        bookOne = wx.Panel(notebook, wx.ID_ANY)
        self.lab1 = wx.StaticText(bookOne, wx.ID_ANY, 
                                  (_("Chart Reading")))
        self.lab2 = wx.StaticText(bookOne, wx.ID_ANY, 
                                  (_("Hands/Foots Setting")))
        self.lab3 = wx.StaticText(bookOne, wx.ID_ANY, 
                                  (_("Rudiments")))
        self.txt1 = wx.TextCtrl(bookOne, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.txt2 = wx.TextCtrl(bookOne, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.txt3 = wx.TextCtrl(bookOne, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.lab4 = wx.StaticText(bookOne, wx.ID_ANY, 
                                  (_("Independance/Coordination")))
        self.lab5 = wx.StaticText(bookOne, wx.ID_ANY, 
                                  (_("Elements of Style Rhythm")))
        self.lab6 = wx.StaticText(bookOne, wx.ID_ANY, 
                                  (_("Minus One")))
        self.txt4 = wx.TextCtrl(bookOne, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.txt5 = wx.TextCtrl(bookOne, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.txt6 = wx.TextCtrl(bookOne, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.lab7 = wx.StaticText(bookOne, wx.ID_ANY, (_("Other-1")))
        self.lab8 = wx.StaticText(bookOne, wx.ID_ANY, (_("Other-2")))
        self.lab9 = wx.StaticText(bookOne, wx.ID_ANY, (_("Other-3")))
        self.txt7 = wx.TextCtrl(bookOne, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.txt8 = wx.TextCtrl(bookOne, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.txt9 = wx.TextCtrl(bookOne, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        #### insert widget in second notebook table
        bookTwo = wx.Panel(notebook, wx.ID_ANY)
        self.lab10 = wx.StaticText(bookTwo, wx.ID_ANY, 
                                   (_("Votes/Report")))
        self.txt10 = wx.TextCtrl(bookTwo, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        self.lab11 = wx.StaticText(bookTwo, wx.ID_ANY, 
                                   (_("Reminder/Block-notes")))
        self.txt11 = wx.TextCtrl(bookTwo, wx.ID_ANY, "", style=wx.TE_MULTILINE)
        btnExit = wx.Button(self, wx.ID_CANCEL, ("&Cancel"))
        self.btnApply = wx.Button(self, wx.ID_APPLY, ("&Apply"))

        #---------------------------------------------- PROPERTIES
        self.datepk.SetMinSize((200, -1))
        self.lab1.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.lab2.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.lab3.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.lab4.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.lab5.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.lab6.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.lab7.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.lab8.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.lab9.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.lab10.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.lab11.SetFont(wx.Font(9, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.txt11.SetBackgroundColour('#fff96f')#yellow
        self.btnApply.Disable()
        #-------------------------------------------------- LAYOUT
        sizBase = wx.BoxSizer(wx.VERTICAL)
        sizTop = wx.FlexGridSizer(1, 3, 0, 40)
        self.boxDate = wx.StaticBoxSizer(self.boxDate, wx.VERTICAL)
        self.boxDate.Add(self.datepk, 0, wx.ALIGN_CENTER | wx.ALL, 0)
        sizTop.Add(self.enableLesson, 1, wx.ALIGN_CENTER|wx.ALL, 10)
        sizTop.Add(self.boxDate, 1, wx.EXPAND|wx.ALL, 10)
        sizTop.Add(self.rdb, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        sizBase.Add(sizTop,0, wx.TOP|wx.BOTTOM,10)
        
        # BOOK One
        sizBookOne = wx.GridSizer(6, 3, 0, 0)
        #### Set first table of notebook
        sizBookOne.Add(self.lab1, 0, wx.ALIGN_CENTER, 0)
        sizBookOne.Add(self.lab2, 0, wx.ALIGN_CENTER, 0)
        sizBookOne.Add(self.lab3, 0, wx.ALIGN_CENTER, 0)
        sizBookOne.Add(self.txt1, 0, wx.EXPAND|wx.ALL, 5)
        sizBookOne.Add(self.txt2, 0, wx.EXPAND|wx.ALL, 5)
        sizBookOne.Add(self.txt3, 0, wx.EXPAND|wx.ALL, 5)
        sizBookOne.Add(self.lab4, 0, wx.ALIGN_CENTER, 0)
        sizBookOne.Add(self.lab5, 0, wx.ALIGN_CENTER, 0)
        sizBookOne.Add(self.lab6, 0, wx.ALIGN_CENTER, 0)
        sizBookOne.Add(self.txt4, 0, wx.EXPAND|wx.ALL, 5)
        sizBookOne.Add(self.txt5, 0, wx.EXPAND|wx.ALL, 5)
        sizBookOne.Add(self.txt6, 0, wx.EXPAND|wx.ALL, 5)
        sizBookOne.Add(self.lab7, 0, wx.ALIGN_CENTER, 0)
        sizBookOne.Add(self.lab8, 0, wx.ALIGN_CENTER, 0)
        sizBookOne.Add(self.lab9, 0, wx.ALIGN_CENTER, 0)
        sizBookOne.Add(self.txt7, 0, wx.EXPAND|wx.ALL, 5)
        sizBookOne.Add(self.txt8, 0, wx.EXPAND|wx.ALL, 5)
        sizBookOne.Add(self.txt9, 0, wx.EXPAND|wx.ALL, 5)
        bookOne.SetSizer(sizBookOne)
        notebook.AddPage(bookOne, (_("Studies Topic")))
        
        # BOOK Two
        sizBookTwo = wx.FlexGridSizer(2, 2, 0, 0)
        #### Set second table of notebook
        sizBookTwo.Add(self.lab10, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        sizBookTwo.Add(self.lab11, 0, wx.ALIGN_CENTER|wx.ALL, 5)
        sizBookTwo.Add(self.txt10, 1, wx.EXPAND|wx.ALL, 5)
        sizBookTwo.Add(self.txt11, 1, wx.EXPAND|wx.ALL, 5)
        bookTwo.SetSizer(sizBookTwo)
        notebook.AddPage(bookTwo, (_("Votes and Reminders")))
        sizBookTwo.AddGrowableRow(1)
        sizBookTwo.AddGrowableCol(0)
        sizBookTwo.AddGrowableCol(1)

        ####  add notebook to sizBase
        sizBase.Add(notebook, 1, wx.EXPAND, 5)
        
        #### set sizer bottom
        sizBottom = wx.GridSizer(1, 2, 0, 0)
        #sizBottom.Add(btnExit, 0, wx.ALIGN_LEFT | wx.ALL, 5)
        #sizBottom.Add(self.btnApply, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        sizBottom.Add(btnExit, 0, wx.ALL, 5)
        sizBottom.Add(self.btnApply, 0, wx.ALL, 5)
        #sizBase.Add(sizBottom, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 5)
        sizBase.Add(sizBottom,flag=wx.ALL|wx.ALIGN_RIGHT|wx.RIGHT, border=5)
        
        self.SetSizer(sizBase)
        #sizBase.Fit(self)

        self.currdate = self.datepk.GetValue()
        self.OnStart(self)
        
        ######################## binding #####################
        self.Bind(wx.EVT_TOGGLEBUTTON, self.OnStart, self.enableLesson)
        self.Bind(wx.adv.EVT_DATE_CHANGED, self.onDate, self.datepk)
        self.Bind(wx.EVT_RADIOBOX, self.onAbsences, self.rdb)
        btnExit.Bind(wx.EVT_BUTTON, self.on_close)
        self.Bind(wx.EVT_BUTTON, self.onApply, self.btnApply)

        
    ######################## Events Handler
    def OnStart(self, event):
        """
        Enable or disable all widgets for subscribe a new lesson
        """
        txt = [self.txt1, 
               self.txt2, 
               self.txt3, 
               self.txt4, 
               self.txt5, 
               self.txt6,
               self.txt7, 
               self.txt8, 
               self.txt9, 
               self.txt10,
               self.txt11,
               ]
        lab = [self.lab1, 
               self.lab2, 
               self.lab3, 
               self.lab4, 
               self.lab5, 
               self.lab6,
               self.lab7, 
               self.lab8, 
               self.lab9,
               self.lab10,
               self.lab11,
               ]
        if self.enableLesson.GetValue():
            [a.Enable() for a in txt]
            [a.Enable() for a in lab]
            self.datepk.Enable(), self.boxDate.GetStaticBox().Enable() 
            self.rdb.Enable(), self.btnApply.Enable()
        else:
            [a.Disable() for a in txt]
            [a.Disable() for a in lab]
            [a.SetValue('') for a in txt]
            self.datepk.Disable(), self.boxDate.GetStaticBox().Disable()
            self.rdb.Disable(), self.btnApply.Disable()

    #-----------------------------------------------------------------------#
    def onDate(self, event):
        self.currdate = self.datepk.GetValue()
    #-----------------------------------------------------------------------#
    def onAbsences(self, event):
        """
        Enable or disable widget in sizBookOne only, when radiobox 
        is check. To prevent repetitive processes for Enable() and 
        Disable() methods i have not been able (or I did not want) 
        to find better solution that self.switch
        """
        #14/12/2017 Ho aggiunto le list comprehension per ridurre 
        #le linee fisiche di codice
        txt = [self.txt1, 
               self.txt2, 
               self.txt3, 
               self.txt4, 
               self.txt5, 
               self.txt6,
               self.txt7, 
               self.txt8, 
               self.txt9 
               ]
        lab = [self.lab1, 
               self.lab2, 
               self.lab3, 
               self.lab4, 
               self.lab5, 
               self.lab6,
               self.lab7, 
               self.lab8, 
               self.lab9 
               ]
        
        if self.rdb.GetSelection() == 0:
            if self.switch:
                self.switch = False
                [a.Enable() for a in txt]# da 1 a 9
                [a.Enable() for a in lab]# da 1 a 9

        elif self.rdb.GetSelection() == 1 or self.rdb.GetSelection() == 2:
            if not self.switch:
                self.switch = True
                [a.SetValue('') for a in txt]# da 1 a 9
                [a.Disable() for a in txt]# da 1 a 9
                [a.Disable() for a in lab]# da 1 a 9
                
    #-----------------------------------------------------------------------#
    def onApply(self, event):
        """
        Save the lesson to db in Lesson table.
        """
        msg = (_("Insert lesson in the database ?"))
        if wx.MessageBox(msg, 
                         _("DrumsT: Please confirm"), 
                         wx.ICON_QUESTION | 
                         wx.YES_NO) == wx.NO:
            return
        
        absences = u"%s" % (self.rdb.GetItemLabel(self.rdb.GetSelection()))
        date = "%s" % (self.currdate)
        arg1 = """%s""" % (self.txt1.GetValue().strip())
        arg2 = """%s""" % (self.txt2.GetValue().strip())
        arg3 = """%s""" % (self.txt3.GetValue().strip())
        arg4 = """%s""" % (self.txt4.GetValue().strip())
        arg5 = """%s""" % (self.txt5.GetValue().strip())
        arg6 = """%s""" % (self.txt6.GetValue().strip())
        arg7 = """%s""" % (self.txt7.GetValue().strip())
        arg8 = """%s""" % (self.txt8.GetValue().strip())
        arg9 = """%s""" % (self.txt9.GetValue().strip())
        arg10 = """%s""" % ( self.txt10.GetValue().strip())
        arg11 = """%s""" % ( self.txt11.GetValue().strip())

        listObj = [self.IDclass, absences, date, arg1, arg2, arg3, arg4, 
                   arg5, arg6, arg7, arg8, arg9, arg10, arg11, 
                   ]
        for n, item in enumerate(listObj):# if empty str fill out with NONE str
            if item == '':
                listObj[n] = 'NONE'

        lesson = School_Class().lessons(listObj, self.path_db)
        
        if lesson[0]:
            wx.MessageBox(lesson[1],
                          _('DrumsT: Error'), 
                          wx.ICON_ERROR, 
                          self
                          )
            self.btnApply.Disable()
            return
        
        wx.MessageBox(_('DrumsT: Successfully stored!'), 
                      _("Info"), 
                      wx.OK, 
                      self
                      )
        self.btnApply.Disable()
        self.enableLesson.SetValue(False)
        self.OnStart(self)
        
     #-----------------------------------------------------------------------#
    def on_close(self, event):
        #self.parent.Destroy()
        self.parent.on_close(self)
        #event.Skip()

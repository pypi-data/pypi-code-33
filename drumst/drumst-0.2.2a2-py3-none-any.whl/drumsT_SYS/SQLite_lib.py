#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#########################################################
# Name: SQLite_lib.py
# Porpose: read/write access to databases
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

#from __future__ import with_statement
import sqlite3

class School_Class(object):
    """
    Run processes for working with sqlite3: creating, updating, 
    deleting, quering, etc. in a db.

    NOTES: if you want handling last id:
    #cursor.execute('SELECT max(IDyear) FROM School')# by index
    #max_id = cursor.fetchone()[0] # by index
    """
    def __init__(self):
        """
        almost all methods that follow, they use a manage of errors. 
        These attributes are used to check this process:
        self.error is simply boolean. 
        self.msg contains a message if self.error is True
        """
        self.error = False
        self.msg = None
        
    #-------------------------------------------------------------------------#
    def newSchoolyear(self, db_filename, name, year):
        """
        Create new School and Class tables: 
        The 'School' table has one only column with IDyear.
        The Class table is defined by own ID and IDyear of the school.
        Also, this method is used when run DrumsT for first time and there 
        is nothing database/path-name configured, this method set a new one.
        """
        db_filename = '%s/%s/%s.drtDB' % (db_filename, name, name)
        try:
            with sqlite3.connect(db_filename) as conn:
                cursor = conn.cursor()
                # create a table School
                cursor.execute("""CREATE TABLE School (IDyear TEXT)""")
                # insert year in school
                cursor.execute("INSERT INTO School (IDyear) VALUES(?)", [year])
                # create a table Class
                cursor.execute("""CREATE TABLE Class 
                               (IDclass INTEGER PRIMARY KEY AUTOINCREMENT, 
                               IDyear INT, Name TEXT, Surname TEXT, Phone TEXT,
                               Address TEXT, BirthDate TEXT, JoinDate TEXT, 
                               LevelCourse TEXT)
                               """)
                # create a table Lesson
                cursor.execute("""CREATE TABLE Lesson
                               (IDlesson INTEGER PRIMARY KEY AUTOINCREMENT,
                               IDclass INT, Attendance TEXT, Date TEXT, 
                               Reading TEXT, Setting TEXT, Rudiments TEXT,
                               Coordination TEXT, Styles TEXT, Minusone TEXT,
                               Other1 TEXT, Other2 TEXT, Other3 TEXT,
                               Votes TEXT, Notes TEXT)
                               """)
        except Exception as err:
            self.error = True
            self.msg = (_("DrumsT: Failed to create new database\n\n"
                        "ERROR: %s") % err)
            #raise # WARNING: use raise statement for debug only

        return self.error, self.msg
    
    #-----------------------------------------------------------------------#
    def checkstudent(self, Name, Surname, db_filename, IDyear):
        """
        This method must be used before the insertstudent() method to 
        test if there are existance profiles with same match by 
        name and surname.
        """
        conn = sqlite3.connect('%s' % db_filename)
        cursor = conn.cursor()
        
        ctrl = cursor.execute("SELECT * FROM Class WHERE (IDyear=?)", [IDyear])
        for m in ctrl:
            if '%s %s' %(m[2],m[3]) == '%s %s' %(Name,Surname):
                conn.close()
                self.error = True
                self.msg = (_("This name already exists:"
                            "\n\nNAME/SURNAME:  {0} {1}\nPHONE:  {2}\n"
                            "ADDRESS:  {3}\nBIRTHDATE:  {4}\n"
                            "JOINED DATE:  {5}\nLEVEL:  {6}"
                            "\n\nWant you to save anyway?").format(
                            m[2],m[3],m[4],m[5],m[6],m[7],m[8]))
                break
                
        conn.close()
        return self.error, self.msg
    
    #-----------------------------------------------------------------------#
    def insertstudent(self, data, db_filename, IDyear):
        """
        Insert new student profile into Class table.
        """
        try:
            with sqlite3.connect(db_filename) as conn:
                cursor = conn.cursor()
                cursor.execute("""INSERT INTO Class 
                                  (IDyear, Name, Surname, Phone, Address,
                                  BirthDate, JoinDate, LevelCourse) 
                                  VALUES(?,?,?,?,?,?,?,?)
                               """, [IDyear, data[0], data[1], data[2], 
                                     data[3], data[4], data[5], data[6]])
        except Exception as err:
            self.error = True
            self.msg = (_("DrumsT: Failed to insert student in Class table\n\n"
                        "ERROR: %s") % err)
            conn.rollback()
            #raise # WARNING: use raise statement for debug only
            
        else:
            conn.commit()

        return self.error, self.msg
    #----------------------------------------------------------------------#
    def lessons(self, lisT, db_filename):
        """
        Insert a new day lesson into Lesson table
        """
        db_filename = ('%s' % db_filename)
        try:
            with sqlite3.connect(db_filename) as conn:
                cursor = conn.cursor()
                cursor.execute("""INSERT INTO Lesson 
                               (IDclass, Attendance, Date, Reading, Setting, 
                               Rudiments, Coordination, Styles, Minusone, 
                               Other1, Other2, Other3, Votes, Notes) 
                               VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                               """, [lisT[0],lisT[1],lisT[2],lisT[3],lisT[4],
                                    lisT[5],lisT[6],lisT[7],lisT[8],lisT[9],
                                    lisT[10],lisT[11],lisT[12],lisT[13]])
        
        except Exception as err:
            self.error = True
            self.msg = (_("DrumsT: Failed to add lesson in Lesson table\n\n"
                        "ERROR: %s") % err)
            conn.rollback()
            #raise # WARNING: use raise statement for debug only
            
        else:
            conn.commit()

        return self.error, self.msg
    #----------------------------------------------------------------------#
    def showInTable(self, IDclass, db_filename):
        """
        Show all student lessons by selecting IDclass
        """
        conn = sqlite3.connect('%s' % (db_filename))
        cursor = conn.cursor()

        n = cursor.execute("""SELECT * FROM Lesson 
                           WHERE IDclass=?""", [IDclass])
        lesson = []
        for row in n:
            lesson.append(row)

        conn.close()
        return lesson
        
    #-------------------------------------------------------------------------#
    def displayclass(self, db_filename, IDyear):
        """
        Show all class items  by selecting school year
        """
        conn = sqlite3.connect('%s' % (db_filename))
        cursor = conn.cursor()

        n = cursor.execute("""SELECT * FROM Class 
                           WHERE IDyear=?""", [IDyear])
        student = []
        for row in n:
            student.append(row)

        conn.close()
        return student

    #----------------------------------------------------------------------#
    def displayschool(self, db_filename):
        """
        Show all school year by select in the combobox
        """
        conn = sqlite3.connect('%s' % (db_filename))
        
        schools = []
        cursor = conn.execute("SELECT * from School")
        
        for row in cursor:
            schools.append(row)
            
        conn.close()
        return schools

    #----------------------------------------------------------------------#
    def updateyear(self, db_filename, year):
        """
        Insert new date in School if not still exist. If exist raise
        a exception RuntimeError. In all other cases, the exceptions 
        are always reported.
        """
        list_years = []
        try:
            with sqlite3.connect(db_filename) as conn:
                cursor = conn.cursor()
                # find a match error:
                ctrl = cursor.execute("""SELECT * FROM School 
                                      WHERE IDyear=?""", [year])
                for m in ctrl:
                    list_years.append(m[0])
                if year in list_years:
                    raise RuntimeError(_('This school year already exist.'))
                else:
                    # insert year in school:
                    cursor.execute("""INSERT INTO School (IDyear) 
                                   VALUES(?)""", [year])
        except Exception as err:
            self.error = True
            self.msg = (_("DrumsT: Failed to add new school year\n\n"
                        "ERROR: %s") % err)
            conn.rollback()
            #raise # WARNING: use raise statement for debug only
        else:
            conn.commit()

        return self.error, self.msg
    
    #----------------------------------------------------------------------#
    def change_class_item(self, data, IDclass, db_filename):
        """
        Updates existing records in the Class table
        """
        try:
            with sqlite3.connect(db_filename) as conn:
                cursor = conn.cursor()
                cursor.execute("""UPDATE Class SET 
                                  Name=?, Surname=?, Phone=?, Address=?, 
                                  BirthDate=?, JoinDate=?, LevelCourse=? 
                                  WHERE (IDclass=?)
                               """, [data[0], data[1], data[2], data[3],
                                     data[4], data[5], data[6], IDclass])
        except Exception as err:
            self.error = True
            self.msg = (_("DrumsT: Failed to update student in Class table\n\n"
                        "ERROR: %s") % err)
            conn.rollback()
            #raise # WARNING: use raise statement for debug only
        else:
            conn.commit()

        return self.error, self.msg
    
    #----------------------------------------------------------------------#
    def delete_profile(self, IDclass, db_filename):
        """
        cancella records già esistenti
        """
        try:
            with sqlite3.connect(db_filename) as conn:
                cursor = conn.cursor()
                cursor.execute("""DELETE FROM Class 
                                  WHERE (IDclass=?)""", [IDclass])
                cursor.execute("""DELETE FROM Lesson 
                                  WHERE (IDclass=?)""", [IDclass])
        except Exception as err:
            self.error = True
            self.msg = (_("DrumsT: Failed to delete student and its lesson "
                        "in Class table and Lesson table\n\n"
                        "ERROR: %s") % err)
            conn.rollback()
            #raise # WARNING: use raise statement for debug only
        else:
            conn.commit()

        return self.error, self.msg
    
    #----------------------------------------------------------------------#
    def change_lesson_items(self, lisT, db_filename):
        """
        Updates existing records in the Lesson table
        """
        try:
            with sqlite3.connect(db_filename) as conn:
                cursor = conn.cursor()
                cursor.execute("""UPDATE Lesson SET 
                                  Attendance=?, Date=?, Reading=?, Setting=?, 
                                  Rudiments=?, Coordination=?, Styles=?,
                                  Minusone=?, Other1=?, Other2=?, Other3=?, 
                                  Votes=?, Notes=? 
                                  WHERE (IDlesson=?)
                               """, [lisT[2], lisT[3], lisT[4], lisT[5], 
                                     lisT[6], lisT[7], lisT[8], lisT[9], 
                                     lisT[10], lisT[11], lisT[12], lisT[13], 
                                     lisT[14], lisT[0]])
        except Exception as err:
            self.error = True
            self.msg = (_("DrumsT: Failed to update lesson in Lesson table\n\n"
                        "ERROR: %s") % err)
            conn.rollback()
            #raise # WARNING: use raise statement for debug only
        else:
            conn.commit()

        return self.error, self.msg

        #----------------------------------------------------------------------#
        

#     A module that will help user to import tab auto-completion feature to
#     his/her program
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#      Author: Vaisakh Anand (gitlab: @vaisakh032)
#      repo: https://gitlab.com/vaisakh032/tab-auto-completion
# /*******************************************************************************
#  * tabCompletion.py
#  *******************
#   This module will help you to impart tab auto-complete feature into your program
#   details on how to use the program and what each of the functions do is cleary
#   described through the mardown file and through doc strings
#  *********************************************************************************

from pynput.keyboard import Key, Listener, Controller
import sys
import os
import json
import getch
import subprocess
import re


class Tabcomplete:
    """Class that bundle's the data and the functionality required for tab completion
    The variables include:
        -> data : The dictionary that contains the data required for tab completion.
                  Structure: {"typeName1":[possible, values, as list],
                              "typeName2":[possible, vlaues, as list],
                              "typeName3":[possible, vlaues, as list] }

        -> stri : A string which will store the input data which the user enters
        -> stringPosition: variable stores the current string possition
    """
    data = []
    stri = ""
    stringPosition = 0
    path = ""
    keyboard = Controller()
    Listener

    def __init__(self, content):
        """To initialise the object with the required content needed
        for auto completion. To initialise the object you need to provide a
        dictionary that will contain data for auto completion
        Requires two basic parameters
         -> Content : Either the dictionary itself or the path to the json file
                      containing the dictionary
        """

        if type(content) == type(""):
            self.path = content
            if os.path.exists(content):
                with open(content) as f:
                    Tabcomplete.data = json.load(f)
                    Tabcomplete.path = content
            else:
                print("Path defined: ",content," does not exists\n Please check")
                exit()
        elif type(content) == type({}):
            Tabcomplete.data = content
            Tabcomplete.path = -1
        else:
            print("Type of data supplied to object incorrect please specify 'path' or 'dictionary as param'")
            exit(0)

    def move_cursor(direction,pos):
        """Method to print out ascii escape codes for moving manipulating the output
        Requires two parameters:
         -> direction : which denotes what to do.
                        'u' - > move up the cursor
                        'd' - > move down the cursor
                        'r' - > move the cursor to the right
                        'l' - > move the cursor to the left
                        'e' - > erase the present line
                        's' - > move up the cursor to the starting of the line
         -> pos  : denotes the number of times ascii escape has to be printed.
        """
        asci = ""
        if direction == 'u':
            asci = u"\u001b[1A"
        elif direction == 'd':
            asci = u"\u001b[1B"
        elif direction == 'r':
            asci = u"\u001b[1C"
        elif direction == 'l':
            asci = u"\u001b[1D"
        elif direction == 'e':
            asci = u"\033[2K"
        elif direction == 's':
            asci = u"\u001b[1000D"
        for i in range(pos):
            sys.stdout.write(asci)
        sys.stdout.flush()

    def find_common(string1, string2):
        """Method to find the common between two strings.
        Will check the longest string from the params and then find the common
        between both the strings. The function returns the common characters
        found in the string till the very first uncommon is encountered.
        Requires two parameters: string1 and string2 to check for comparisons.
        """
        common = ""
        length = 0
        if len(string1) <len(string2):
            length = len(string1)
        else:
            length =  len(string2)
        #length = lambda a,b: a if (a < b) else b
        for i in range(length):
            if string1[i] == string2[i]:
                common = common + string1[i]
            else:
                break
        return common


    def get_active_window_pid():
        """Method to get the pid of the window which has the focus at the instant
        when the function is invoked.

        Return:
          ->  Returns the pid number of the currently active window
        """
        root = subprocess.Popen(['xprop', '-root', '_NET_ACTIVE_WINDOW'], stdout=subprocess.PIPE)
        stdout, stderr = root.communicate()

        m = re.search(b'^_NET_ACTIVE_WINDOW.* ([\w]+)$', stdout)
        if m != None:
            window_id = m.group(1)
            return window_id
        else:
            return None
        return None


    def tab_complete(searchType, caseSensitive):
        """Method to auto-complete the input given by the user.
        Parameters :
         -> searchType: Denotes the typeName from the dict so that
                        the possible values can be loaded from the
                        corresponding list in the dictionary
         ->  caseSensitive : Denotes wether the program should be
                            case sensitive or not.
        """
        matches = []
        if caseSensitive == 'y':
            for equips in Tabcomplete.data[searchType]:
                if equips.startswith(Tabcomplete.stri):
                    matches.append(equips)
        else:
            for equips in Tabcomplete.data[searchType]:
                if equips.startswith(Tabcomplete.stri.lower()):
                    matches.append(equips)

        if len(matches) is 1 :
            Tabcomplete.stri = matches[0]
        elif len(matches) > 1:
            Set = matches[0]
            for ele in matches:
                Set = str(Tabcomplete.find_common(Set,ele))
            Tabcomplete.stri = Set
            Tabcomplete.print_suggestion(matches)
        else:
            print("\a")

    def print_suggestion(matches):
        """Method to format the output of suggestions computed. The method would
        limit the output text to less than 28 characters to format output.
        """
        oldLen = 0
        print("\n")
        for i, ele in enumerate(matches):
            if len(ele) > 28:
                ele = ele[:30]+".."
            if (i+1)%2 == 0:
                print(" "*(32-oldLen), ele)
            else:
                print(ele,end = " " )
                oldLen = len(ele)
        print("\n")


    def check_for_index(searchType):
        """Method to check if the typeName given is present in the given dictionary
        Requires one parameter: searchType which denotes the typeName from which then
        tab completion will collect the possible values
        """
        if Tabcomplete.stri in Tabcomplete.data[searchType]:
            return True
        else:
            return False

    def updateJson():
        """Method to update the json file given in the path during initialisation.
        This functions helps to update the list of possible values under typeName
        """
        sys.stdout.flush()
        with open(Tabcomplete.path, 'w+') as outfile:
            json.dump(Tabcomplete.data, outfile)

    @staticmethod
    def getip(PrintText,searchFor,caseSensitive = 'n', compulsoryInput = 'y', dynamicUpdation = 'y'):
        """Method to be invoked when the object is initialised.
        This method will help the user to get the input from the user and will
        call the required functions for auto completion.
        Parameters:
         -> PrintText : Text to be printed, which denotes what the user has to
                        enter
         -> searchFor : The typeName which will help get the list of possible
                        values for tab completion from the dictionary
         -> caseSensitive: It denotes wether to tab completion is caseSensitive (y)
                           or not (n - by default)
         -> compulsoryInput: if 'y' The function will terminate on the press of
                            enter only if the string is not empty
         -> dynamicUpdation: If 'y' the function will update the json files as
                            the function encounters a new input.
        Return:
            This method returns the completed inout from the user
        """
        searchType = searchFor
        print("\n")
        sys.stdout.write(PrintText)
        sys.stdout.flush()
        original_window_pid = Tabcomplete.get_active_window_pid()
        get_input = True
        def on_release(key):
            current_window_pid = Tabcomplete.get_active_window_pid()
            if current_window_pid != original_window_pid:
                    get_input = False
            elif current_window_pid == original_window_pid:
                    get_input = True

            if key == Key.tab and get_input is True:
                print("\n")
                Tabcomplete.move_cursor("u",1)
                Tabcomplete.move_cursor("e",1)
                Tabcomplete.tab_complete(searchType,caseSensitive)
                sys.stdout.write(PrintText)
                sys.stdout.write(Tabcomplete.stri)
                sys.stdout.flush()
                return True

            elif key == Key.backspace and get_input is True:
                sys.stdout.write(Tabcomplete.stri)
                Tabcomplete.stri = Tabcomplete.stri[:-1]
                Tabcomplete.move_cursor("e",1)            # erase line
                Tabcomplete.move_cursor("s",1)            # get to the starting
                sys.stdout.write(PrintText)
                sys.stdout.write(Tabcomplete.stri)
                sys.stdout.flush()
                return True

            elif key == Key.enter and get_input is True:
                sys.stdout.flush()
                if Tabcomplete.stri != "":
                    # flush the keyboard buffer
                    while(getch.getch() != '\n'):
                        continue

                    if not Tabcomplete.check_for_index(searchType) and Tabcomplete.path != -1 and dynamicUpdation == 'y': # check if  the possible value is already indexed
                        if caseSensitive == 'n':
                            Tabcomplete.data[searchType].append(Tabcomplete.stri.lower())
                        elif caseSensitive == 'y':
                            Tabcomplete.data[searchType].append(Tabcomplete.stri)
                        Tabcomplete.updateJson()
                    return False
                else:           # if strng is empty
                    if compulsoryInput == 'y':
                        Tabcomplete.move_cursor("e",1)            #erase line
                        Tabcomplete.move_cursor("s",1)            #get to the starting
                        sys.stdout.write(PrintText)
                        sys.stdout.flush()
                        return True
                    else:
                        return False

            elif key == Key.space and get_input is True:
                Tabcomplete.stri = Tabcomplete.stri + " "

            elif str(key).startswith("Key") and get_input is True:
                Tabcomplete.move_cursor("e",1)            #erase line
                Tabcomplete.move_cursor("s",1)            #get to the starting
                sys.stdout.write(PrintText)
                sys.stdout.write(Tabcomplete.stri)
                sys.stdout.flush()
                print("\a", end ="")
                return True
            else:
                if not str(key).startswith("Key") and get_input is True:
                    Tabcomplete.stri = Tabcomplete.stri + str(key).strip("'")
                    Tabcomplete.stringPosition = Tabcomplete.stringPosition + 1
                return True

        with Listener( on_release = on_release) as listener:
            ip = listener.join()
            if not ip:
                temp = Tabcomplete.stri
                Tabcomplete.stri = ""
                if temp == "" :
                    return False
                else:
                    return temp
            else:
                Tabcomplete.stri.append(ip)

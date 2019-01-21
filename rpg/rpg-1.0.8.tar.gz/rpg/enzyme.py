# -*- coding: utf-8 -*-

########################################################################
# Author: Nicolas Maillet                                              #
# Copyright © 2018 Institut Pasteur, Paris.                            #
# See the COPYRIGHT file for details                                   #
#                                                                      #
# This file is part of Rapid Peptide Generator (RPG) software.         #
#                                                                      #
# RPG is free software: you can redistribute it and/or modify          #
# it under the terms of the GNU General Public License as published by #
# the Free Software Foundation, either version 3 of the License, or    #
# any later version.                                                   #
#                                                                      #
# RPG is distributed in the hope that it will be useful,               #
# but WITHOUT ANY WARRANTY; without even the implied warranty of       #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the        #
# GNU General Public License for more details.                         #
#                                                                      #
# You should have received a copy of the GNU General Public license    #
# along with RPG (LICENSE file).                                       #
# If not, see <http://www.gnu.org/licenses/>.                          #
########################################################################

"""Contains class and functions related to enzymes definition and use"""
import os
import re
from pathlib import Path
from rpg import core
from rpg import rule

DEFUSERENZFILE = str(Path.home()) + "/rpg_user.py"

# Create the enzymes_user file if it does not exist
if not os.path.isfile(DEFUSERENZFILE):
    with open(DEFUSERENZFILE, "w") as out_file:
        out_file.write("from rpg import enzyme\nfrom rpg import rule\n"\
                       "from rpg import enzymes_definition"\
                       "\n\nAVAILABLE_ENZYMES_USER = []\nCPT_ENZ = enzymes_de"\
                       "finition.CPT_ENZ\n\n### ENZYMES DECLARATION ###\n")

class Enzyme:
    """Definition of an cleaving enzyme containing specific rules.

    :param id_: id of the enzyme
    :param name: name of the enzyme
    :param rules: cleaving rules
    :param ratio_miscleavage: miscleavage ratio
    :type id_: int
    :type name: str
    :type rules: list(:py:class:`~rpg.rule.Rule`)
    :type ratio_miscleavage: float
    """
    def __init__(self, id_, name, rules, ratio_miscleavage=0):
        self.id_ = id_
        self.name = name
        self.ratio_miscleavage = ratio_miscleavage
        self.rules = rules

    # self representation for print
    def __repr__(self):
        return "Id: %s\nName: %s\nRatio Miscleavage: %.2f%%\nRules: %s\n" %\
            (self.id_, self.name, self.ratio_miscleavage, self.rules)

    # Equality between two Enzymes
    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    # Needed with __eq__ to make it hashable
    def __hash__(self):
        return hash(self.__dict__.values())

    def write_enzyme_in_user_file(self, enz_file=DEFUSERENZFILE):
        """Write enzyme to user's enzyme file as a Python function.

        :param enz_file: location of user file (default: ~/rpg_user.py)
        :type enz_file: str
        """
        if self.rules != []:
            # Comment and first line of the Enzyme
            ret = "\n\n\n# User-defined enzyme " + self.name + "\nENZ = []\n\n"
            # Write all the main rules and their su-rules
            for i in self.rules:
                ret += i.format_rule()
            # Write the end of the Enzyme
            ret += "ENZYME = enzyme.Enzyme(CPT_ENZ, \"" + self.name + "\", "\
                   "ENZ, 0)\n# Add it to available enzymes\nAVAILABLE_ENZYMES"\
                   "_USER.append(ENZYME)\nCPT_ENZ += 1\n"
            # Write all in the user file
            try:
                with open(enz_file, "a") as output_file:
                    output_file.write(ret)
            except IOError:
                core.handle_errors("'%s' can't be open in '%s' mode" %
                                   (enz_file, "a"), 0, "File ")

def check_enzyme_name(name_new_enz, all_name_enz):
    """Validate the name of a new enzyme.

    :param name_new_enz: name of the new enzyme
    :param all_name_enz: names of already created enzymes
    :type name_new_enz: str
    :type all_name_enz: list(str)

    :return: True if name is correct
    :rtype: bool

    Enzyme name should not contains whitespace character (' ', \\\\t,
    \\\\n, \\\\r, \\\\f, \\\\v), be empty or be already used.
    """

    ret = True
    # If the enzyme name is already taken
    if name_new_enz in all_name_enz:
        core.handle_errors("This name exist, please choose another name.", 2)
        ret = False

    # Does it contain ' ' character?
    res = re.search(" ", name_new_enz)
    if res:
        to_print = ""
        for _ in range(res.start()):
            to_print += " "
        to_print += "^\n"
        core.handle_errors(to_print + "Space character found at position " +
                           str(res.start() + 1) +
                           ", please choose another name.", 2)
        ret = False

    # Does it contain \t character?
    res = re.search("\t", name_new_enz)
    if res:
        to_print = ""
        for _ in range(res.start()):
            to_print += " "
        to_print += "^\n"
        core.handle_errors(to_print + "Tab character found at position " +
                           str(res.start() + 1) +
                           ", please choose another name.", 2)
        ret = False
    res = name_new_enz.find("\\t")
    if res != -1:
        to_print = ""
        for _ in range(res):
            to_print += " "
        to_print += "^\n"
        core.handle_errors(to_print + "Tab character found at position " +
                           str(res + 1) + ", please choose another name.", 2)
        ret = False

    # Does it contain \n character?
    res = re.search("\n", name_new_enz)
    if res:
        to_print = ""
        for _ in range(res.start()):
            to_print += " "
        to_print += "^\n"
        core.handle_errors(to_print + "Newline character found at position " +
                           str(res.start() + 1) +
                           ", please choose another name.", 2)
        ret = False
    res = name_new_enz.find("\\n")
    if res != -1:
        to_print = ""
        for _ in range(res):
            to_print += " "
        to_print += "^\n"
        core.handle_errors(to_print + "Newline character found at position " +
                           str(res + 1) + ", please choose another name.", 2)
        ret = False

    # Does it contain \r character?
    res = re.search("\r", name_new_enz)
    if res:
        to_print = ""
        for _ in range(res.start()):
            to_print += " "
        to_print += "^\n"
        core.handle_errors(to_print + "Carriage return (\\r) character found "
                           "at position " + str(res.start() + 1) +
                           ", please choose another name.", 2)
        ret = False
    res = name_new_enz.find("\\r")
    if res != -1:
        to_print = ""
        for _ in range(res):
            to_print += " "
        to_print += "^\n"
        core.handle_errors(to_print + "Carriage return (\\r) character found "
                           "at position " + str(res + 1) +
                           ", please choose another name.", 2)
        ret = False

    # Does it contain \f character?
    res = re.search("\f", name_new_enz)
    if res:
        to_print = ""
        for _ in range(res.start()):
            to_print += " "
        to_print += "^\n"
        core.handle_errors(to_print + "Form feed (\\f) character found at "
                           "position " + str(res.start() + 1) +
                           ", please choose another name.", 2)
        ret = False
    res = name_new_enz.find("\\f")
    if res != -1:
        to_print = ""
        for _ in range(res):
            to_print += " "
        to_print += "^\n"
        core.handle_errors(to_print + "Form feed (\\f) character found at "
                           "position " + str(res + 1) +
                           ", please choose another name.", 2)
        ret = False

    # Does it contain \v character?
    res = re.search("\v", name_new_enz)
    if res:
        to_print = ""
        for _ in range(res.start()):
            to_print += " "
        to_print += "^\n"
        core.handle_errors(to_print + "Vertical Tab (\\v) character found at "
                           "position " + str(res.start() + 1) +
                           ", please choose another name.", 2)
        ret = False
    res = name_new_enz.find("\\v")
    if res != -1:
        to_print = ""
        for _ in range(res):
            to_print += " "
        to_print += "^\n"
        core.handle_errors(to_print + "Vertical Tab (\\v) character found at "
                           "position " + str(res + 1) +
                           ", please choose another name.", 2)
        ret = False

    # Not empty
    if name_new_enz == "":
        core.handle_errors("Please choose a not empty name.", 2)
        ret = False

    return ret

# Not tested
def user_creation_enzyme(all_enzymes):
    """Text-mod form to input a new enzyme.

    .. warning:: Not tested
    .. warning:: It could be a problem to immediately use the new enzyme (see in-code warning)
    """
    add_enzyme = "y"

    # All enzymes name
    all_name_enz = set()

    # Get all used names
    for enz in all_enzymes:
        all_name_enz.add(enz.name)

    # Adding enzyme
    while add_enzyme == "y":

        # Name of the enzyme
        name_new_enz = input("Name of the new enzyme?\n")
        while not check_enzyme_name(name_new_enz, all_name_enz):
            # Name of the enzyme
            name_new_enz = input("Name of the new enzyme?\n")

        # All the rules entered by user
        all_rules = {}
        # Input of user for creating rules
        def_rule = "_"
        while def_rule != "":
            # Type of rule?
            cutmp = ""
            # Ensure we got a correct value i.e. c, e or q
            while (cutmp != "c") and (cutmp != "e") and (cutmp != "q"):
                cutmp = input("Create a cleaving rule (c) or an exception (e)?"
                              " (q) to quit:\n")
            # Exit
            if cutmp == "q":
                break
            # Set the cut to what the user ask: e = False
            cut = False
            # c = True
            if cutmp == "c":
                cut = True
            # The rule is valid?
            validate_rule = ""
            # Until the rules is not properly defined:
            while validate_rule == "":
                # Cleaving rule
                if cut:
                    def_rule = input("Write your cleaving rule,"
                                     " (q) to quit:\n")
                # Exception rule
                else:
                    def_rule = input("Write your exception rule,"
                                     " (q) to quit:\n")
                # Quit?
                if def_rule == "q":
                    break
                # Check if input is coherent
                validate_rule = rule.check_rule(def_rule)
            # Add this rule
            if validate_rule != "":
                all_rules[validate_rule] = cut

        # Get all the rules in correct format
        correct_rules = rule.create_rules(all_rules)

        # Create the enzyme with fake id (auto-inc)
        # .. warning:: It could be a problem to immediately use the new enzyme
        new_enz = Enzyme(-1, name_new_enz, correct_rules)

        # Write in the user-defined enzymes file
        new_enz.write_enzyme_in_user_file()

        # Add it to known names
        all_name_enz.add(new_enz.name)

        # End of this new enzyme
        add_enzyme = input("Add another enzyme? (y/n)\n")

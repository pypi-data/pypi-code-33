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

"""Contains class and functions related to definition of
cleaving rules
"""
import re
from collections import defaultdict
from rpg import core

class Rule:
    """Definition of a principal rule defining where a cleavage occurs.

    :param index: position where to look for a specific amino acid
    :param letter: amino acid to look for
    :param cut: cut or not at this position on this amino acid
    :param pos: cut before (0) of after (1) amino acid. -1 for unused value
    :type index: signed int
    :type letter: char
    :type cut: bool
    :type pos: int

    :var rules: additional sub-rules of this rule
    :vartype rules: list(:py:class:`Rule`)
    """
    def __init__(self, index, letter, cut, pos):
        self.index = index  # where to look for this aa?
        self.letter = letter  # the aa
        self.cut = cut  # if letter detected at index, cut or not?
        self.pos = pos  # cut before (0) of after (1) letter (-1 if not used)
        self.rules = []  # List of additional rules

    # self representation for print
    # lvl handle number of '\t' needed
    def __repr__(self, lvl=0):
        ret = ""
        for _ in range(lvl):
            ret += "\t"
        ret += "index=" + str(self.index) + "\n"
        for _ in range(lvl):
            ret += "\t"
        ret += "letter=" + str(self.letter) + "\n"
        for _ in range(lvl):
            ret += "\t"
        ret += "cut=" + str(self.cut) + "\n"
        for _ in range(lvl):
            ret += "\t"
        ret += "pos=" + str(self.pos) + "\n"
        # Sub-rules
        for i in self.rules:
            ret += str(i.__repr__(lvl + 1))
        return ret

    # Equality between two Rules
    def __eq__(self, other):
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    # Needed with __eq__ to make it hashable
    def __hash__(self):
        return hash(self.__dict__.values())

    def equ(self, other):
        """Test equality with another rule **without taking into
        account sub-rules nor `cut`**.

        :param other: rule to compare with
        :type other: :py:class:`Rule`

        :return: `True` if rules are equal, `False` otherwise
        :rtype: bool

        :note: use '==' for complete equality including sub-rules.
        """
        return (self.index == other.index) and (self.letter == other.letter) \
            and (self.pos == other.pos)

    def contains(self, other):
        """Test if another rule is contains in sub-rules **without
        taking into account sub-rules nor `cut`** and return the
        sub-rule if founded.

        :param other: rule to compare with
        :type other: :py:class:`Rule`

        :return: the sub-rule is founded, `None` otherwise
        :rtype: :py:class:`Rule`
        """
        ret = None
        for i in self.rules:
            if i.equ(other):
                ret = i
        return ret

    def contains_any_level(self, other, ret=False):
        """Test if another rule is contains within **without taking into
        account sub-rules nor `cut`** no matter what level.

        :param other: rule to compare with
        :type other: :py:class:`Rule`
        :param ret: previous `ret` value (default: `False`)
        :type ret: bool

        :return: `True` if rule is included, `False` otherwise
        :rtype: bool
        """
        for i in self.rules:
            if i.equ(other):
                ret = True
            else:
                ret = i.contains_any_level(other, ret)
        return ret

    def get_header(self):
        """Format header of the rule in Python.

        :return: header of this rule in Python
        :rtype: str
        """
        return 'rule.Rule(' + str(self.index) + ', "' + str(self.letter) + \
            '", ' + str(self.cut) + ', ' + str(self.pos) + ')'

    def get_all_headers(self):
        """Format header of the rule and sub-rules in Python.

        :return: the complete header in Python
        :rtype: str
        """
        ret = []
        # Header of this rule
        ret.append(self.get_header())
        # Sub-rules
        for i in self.rules:
            ret.append(i.get_all_headers())
        return ret

    def format_a_rule(self, prev_name, prev_com):
        """Format the rule in Python.

        :param prev_name: name of the upper rule
        :param prev_com: comment of the upper rule
        :type prev_name: str
        :type prev_com: str

        :return: this rule in Python
        :rtype: str
        """
        ret = []
        # Var name
        if prev_name == "":
            # No prev name, add the pos to the name
            ret_name = str(self.pos).upper()
        else:
            ret_name = prev_name
        # Should we add the new letter of the rule before or
        # after the prev_name?
        if self.index > 0:
            ret_name += self.letter
        elif not ret_name:
            ret_name = self.letter
        else:
            ret_name = self.letter + "_" + ret_name
        # Add the index on the name to avoid same name
        if self.index != 0:
            ret_name += str(self.index)
        # Change '-' to 'm'
        ret_name = ret_name.replace("-", "M")
        # Comment
        ret_com = prev_com
        # Modify the prev_com if needed
        if prev_com != " # ":
            if self.cut:
                ret_com = ret_com.replace("Never", "Always")
            else:
                ret_com = ret_com.replace("Always", "Never")
            # Order of letter
            if self.index > 0:
                ret_com = ret_com.replace(", except...", ", followed by " +
                                          self.letter + ", except...")
            else:
                ret_com = ret_com.replace(", except...", ", preceded by " +
                                          self.letter + ", except...")
        # First comment
        else:
            ret_com += "Always" if self.cut else "Never"
            ret_com += " cleaves "
            ret_com += "after " if self.pos > 0 else "before "
            ret_com += self.letter
            ret_com += ", except..."
        # Full line to write
        ret_total = ret_name + " = " + self.get_header() + ret_com
        # Return all of those
        ret.append(ret_name)
        ret.append(ret_com)
        ret.append(ret_total)
        return ret

    def format_rule(self, prev_name="", prev_com=" # "):
        """Format the whole rule, including sub-rules, in Python,
        ready to be written.

        :param prev_name: name of the upper rule
        :param prev_com: comment of the upper rule
        :type prev_name: str
        :type prev_com: str

        :return: the whole rule in Python
        :rtype: str
        """
        # It is on a enzyme function, we need indentation
        ret = ""
        # Get this rule
        tmp = self.format_a_rule(prev_name, prev_com)
        # Write the line of the rule
        ret += tmp[2] + "\n"
        # Sub-rules:
        for i in self.rules:
            # Pass the current name and comment of this rule
            ret += i.format_rule(tmp[0], tmp[1])
        # Not a main rule
        if prev_name != "":
            # Add this rule to its upper-rule
            ret += prev_name + ".rules.append(" + tmp[0] + ")\n"
        # Main rule
        else:
            # Add it to the return of the enzyme function
            ret += "ENZ.append(" + tmp[0] + ")\n\n"
        return ret


def check_rule(exprule):
    """Check if a rule is properly inputed.

    :param exprule: the raw expression of a rule
    :type exprule: str

    :return: `exprule` if it is correct, empty char otherwise
    :rtype: str
    """

    # Get everything in UPPER
    clean_exprule = exprule.upper()
    # Get " or " in lower
    clean_exprule = clean_exprule.replace(" OR ", " or ")
    ret = clean_exprule

    # Do we got at least one amino acid?
    res = re.search("[A-Za-z]", clean_exprule)
    if not res:
        core.handle_errors("No amino acid founded")
        ret = ""

    # Check all characters
    res = re.search(r"[^A-Za-z ,\(\)]", clean_exprule)
    if res:
        core.handle_errors(", bad character founded at position " +
                           str(res.start() + 1), 2, "Error")
        core.handle_errors(exprule, 2)
        to_print = ""
        for i in range(res.start()):
            to_print += " "
        core.handle_errors(to_print + "^", 2)
        ret = ""

    # No space except before and after "or"
    if ret != "":
        res = re.search(r"(?<!r) (?!o)", clean_exprule)
        if res:
            core.handle_errors(", bad space character founded at position " +
                               str(res.start() + 1), 2, "Error")
            core.handle_errors(exprule, 2)
            to_print = ""
            for i in range(res.start()):
                to_print += " "
            core.handle_errors(to_print + "^", 2)
            ret = ""

    # No letter after a letter (all UPPER except or)
    if ret != "":
        res = re.search(r"[A-Z][A-Z]", clean_exprule)
        if res:
            core.handle_errors(", too many character founded at position " +
                               str(res.start() + 1), 2, "Error")
            core.handle_errors(exprule, 2)
            to_print = ""
            for i in range(res.start() + 1):
                to_print += " "
            core.handle_errors(to_print + "^", 2)
            ret = ""

    # Bracket verif
    if ret != "":
        opening = False
        if "(" not in clean_exprule:
            core.handle_errors(", no opening bracket founded", 2, "Error")
            ret = ""
        else:
            for i, _ in enumerate(clean_exprule):
                # Opening bracket
                if clean_exprule[i] == "(":
                    # If we found another opening but no closing
                    if opening:
                        core.handle_errors(", opening bracket founded without "
                                           "closed one at position " +
                                           str(i + 1), 2, "Error")
                        core.handle_errors(exprule, 2)
                        to_print = ""
                        for _ in range(i):
                            to_print += " "
                        core.handle_errors(to_print + "^", 2)
                        ret = ""
                    else:
                        opening = True
                # Closing bracket
                if clean_exprule[i] == ")":
                    # Seems ok
                    if opening:
                        opening = False
                    else:
                        core.handle_errors(", closing bracket founded without "
                                           "opening before at position " +
                                           str(i + 1), 2, "Error")
                        core.handle_errors(exprule, 2)
                        to_print = ""
                        for _ in range(i):
                            to_print += " "
                        core.handle_errors(to_print + "^", 2)
                        ret = ""
        if opening is True:
            core.handle_errors(", an opened bracket was never closed", 2,
                               "Error")
            ret = ""

    # comma verif: max two and in the same bracket system, and min one
    if ret != "":
        if clean_exprule.count(',') > 2:
            core.handle_errors(", too many ',' founded", 2, "Error")
            ret = ""
        elif clean_exprule.count(',') == 0:
            core.handle_errors(", no ',' founded", 2, "Error")
            ret = ""
        else:
            # comma always closed to a bracket
            res = re.search(r"(?<!\(),(?!\))", clean_exprule)
            if res:
                core.handle_errors(", bad comma founded at position " +
                                   str(res.start() + 1), 2, "Error")
                core.handle_errors(exprule, 2)
                to_print = ""
                for i in range(res.start()):
                    to_print += " "
                core.handle_errors(to_print + "^", 2)
                ret = ""
            # If two commas, they should be in the same bracket system
            comma_found = False
            closed_bracket = False
            for i, _ in enumerate(clean_exprule):
                # First comma
                if clean_exprule[i] == ",":
                    comma_found = True
                # Closing bracket before the first comma
                if comma_found and clean_exprule[i] == ")":
                    closed_bracket = True
                # If we found another comma after the closed bracket
                if comma_found and closed_bracket and clean_exprule[i] == ",":
                    core.handle_errors(", bad comma founded at position " +
                                       str(i + 1), 2, "Error")
                    core.handle_errors(exprule, 2)
                    to_print = ""
                    for _ in range(i):
                        to_print += " "
                    core.handle_errors(to_print + "^", 2)
                    ret = ""
    return ret

def split_complex_rule(a_rule):
    """Split a complex rules containing ' or ' into simpler rules.

    :param a_rule: the rule to split
    :type a_rule: str

    :return: the simple rules
    :rtype: list(str)
    """

    # Returned cleaned rules
    clean_rules = []
    # Does it contains a " or "?
    tmp = a_rule.find(" or ")
    if tmp != -1:
        # Get the beginning
        beg = a_rule[:tmp - 1]
        # Get the end: it start at the next ")" after " or "
        endpos = tmp + a_rule[tmp:].find(")")
        # end is the next ")" and what's following
        end = a_rule[endpos:]
        # It might have a "," before
        if a_rule[endpos - 1] == ",":
            end = "," + end
        # first rule (left side of " or ")
        tmp_rule = beg + a_rule[tmp - 1] + end
        # clean this new rule
        clean_rules += split_complex_rule(tmp_rule)
        # second rule (right side of " or ")
        tmp_rule = beg + a_rule[tmp + 4:]
        # clean this new rule
        clean_rules += split_complex_rule(tmp_rule)
    # No " or " founded
    else:
        # add it to return
        clean_rules.append(a_rule)
    return clean_rules

def add_rule(rules_list, a_rule):
    """Add (recursively) a rule to a list of rules.

    :param rules_list: the list of rules where to add
    :param a_rule: the rule to add
    :type rules_list: list(:py:class:`Rule`)
    :type a_rule: :py:class:`Rule`

    .. warning:: Modify `rules_list` :python:
    """

    # Should we add this rule to this rules_list?
    to_add = True
    # Does this rules already exist in list?
    for i in rules_list:
        # Same content except for sub-rules?
        if i.equ(a_rule):
            # This rules exist
            to_add = False
            # Check the sub-rules of the rule to add
            for j in a_rule.rules:
                add_rule(i.rules, j)
        # Does a sub rules of this rules exist as a rule?
        else:
            # Tmp set for removing inside a for loop
            to_remove = set()
            # For each sub-rules of the rule to add
            for k in a_rule.rules:
                # If this sub-rules is in the rule list, we need to
                # change the rule according to the sub-rule
                # that already exist
                # Same content except for sub-rules?
                if k.equ(i):
                    # This rules exist
                    to_add = False
                    # Flag this conflicting rules
                    to_remove.add(k)
                    # Edit the rule
                    a_rule.cut = not a_rule.cut
                    # Add it to the sub-rule that already exist
                    # without modifying it
                    add_rule(i.rules, a_rule)
            # Remove conflicting rules
            for k in to_remove:
                a_rule.rules.remove(k)
    # This rules is new
    if to_add:
        rules_list.append(a_rule)

def create_rules(all_rules):
    """Create proper rules for an enzyme from raw rules.

    :param all_rules: rules corresponding to the enzyme
    :type all_rules: list(:py:class:`Rule`)

    :return: rules ready to populate an :py:class:`~rpg.enzyme.Enzyme`
    :rtype: list(:py:class:`Rule`)

    This function handle ' or ' keywords, multiple brackets, sort the
    simples rules, create sub-rules, etc. The output is ready to be used
    to create an :py:class:`~rpg.enzyme.Enzyme`.
    """

    # All rules correctly added, ready to be printed
    correct_rules = []
    # handle " or " keyword and split it into several rules
    for tmp_rule, tmp_cut in list(all_rules.items()):
        # Remove this rule from main list
        all_rules.pop(tmp_rule)
        # Split this rule on " or "
        tmp_rules = split_complex_rule(tmp_rule)
        # Add all the cleaned rules corresponding
        for rul in tmp_rules:
            all_rules[rul] = tmp_cut

    # handle multiple "," in one bracket so we got only ONE "," per rule
    for tmp_rule, tmp_cut in list(all_rules.items()):
        if tmp_rule.count(",") > 1:
            # Remove this complex rule
            all_rules.pop(tmp_rule)
            # Modified beginning and ending of the rules to create
            # Beginning of the complex rule
            begpos = tmp_rule.find("(,")
            # Should be like ...('
            beg_cut = tmp_rule[:begpos + 2]
            # Should be like ...(
            beg_no_cut = tmp_rule[:begpos + 1]
            # Ending of the complex rule
            endpos = tmp_rule.find(",)")
            # Should be like ...')
            end_cut = tmp_rule[endpos:]
            # Should be like ...)
            end_no_cut = tmp_rule[endpos + 1:]
            # Add rules
            all_rules[beg_cut + tmp_rule[begpos + 2] + end_no_cut] = tmp_cut
            all_rules[beg_no_cut + tmp_rule[begpos + 2] + end_cut] = tmp_cut

    # Sort rules, smaller first
    all_rules_keys = list(all_rules.keys())
    all_rules_keys.sort(key=lambda s: len(s))

    exceptions = []

    # For each rules
    for rul in all_rules_keys:
        # Split each amino acid of the rule
        tmp_rule = rul.split("(")
        # Remove first i.e. ""
        tmp_rule.pop(0)
        # Remove residual ')' and find the cleaving zone
        for i, _ in enumerate(tmp_rule):
            tmp_rule[i] = tmp_rule[i].replace(")", "")
            if "," in tmp_rule[i]:
                ind = i

        # Dict of pos/val of this rule
        dict_rule = {}
        for i, val in enumerate(tmp_rule):
            # None empty brackets
            if val != '':
                dict_rule[i - ind] = val
        # All positions except the cleaving one
        dict_rule_no_main = dict_rule.copy()
        dict_rule_no_main.pop(0)

        # Create rule for the cleaving zone
        if dict_rule[0][0] == ",":
            # Before letter
            cleaving_zone = Rule(0, str(dict_rule[0][1]), all_rules[rul], 0)
        else:
            # After letter
            cleaving_zone = Rule(0, str(dict_rule[0][0]), all_rules[rul], 1)

        # Is there sub-rule?
        if len(dict_rule) > 1:
            # Reverse the cutting boolean
            cleaving_zone.cut = not cleaving_zone.cut

        # Upper-rule
        previous_rule = cleaving_zone
        # Only the deeper rule should have the correct boolean
        cleav = not all_rules[rul]
        # Exceptions to handle
        if cleaving_zone.cut and len(dict_rule) > 1:
            # Backup this exception
            exceptions.append(dict_rule)
        # No exception
        else:
            # Parse all after cleaving site first
            for i in reversed(sorted(dict_rule_no_main.keys())):
                # Find the deepest rule: left if exist, otherwise, right
                min_key = min(dict_rule_no_main.keys()) # Deep on left
                max_key = max(dict_rule_no_main.keys()) # Deep on right
                if min_key < 0: # Something left, change it (leftest)
                    if i == min_key:
                        cleav = not cleav
                else: # Nothing left, change deepest rule at right
                    if i == max_key:
                        cleav = not cleav
                # Create the rule
                this_rule = Rule(i, dict_rule_no_main[i], cleav, -1)
                # Add this rule to upper-rule
                if not previous_rule.equ(this_rule) and\
                   not previous_rule.contains_any_level(this_rule):
                    previous_rule.rules.append(this_rule)
                # Current rule is the new down-rule
                previous_rule = this_rule
            # Create the corresponding rule
            add_rule(correct_rules, cleaving_zone)

    # Handling exceptions
    for dict_exc in exceptions:
        # Create rule for the cleaving zone
        if dict_exc[0][0] == ",":
            # Before letter
            cleaving_zone = Rule(0, str(dict_exc[0][1]), all_rules[rul], 0)
        else:
            # After letter
            cleaving_zone = Rule(0, str(dict_exc[0][0]), all_rules[rul], 1)

        # Default main_rule
        main_rule = cleaving_zone
        # Find correct main rule in correct_rule
        for corrule in correct_rules:
            # We are in the correct rule
            if corrule.equ(cleaving_zone):
                main_rule = corrule
        # Remove the main rule from it
        dict_exc_no_main = dict_exc.copy()
        dict_exc_no_main.pop(0)

        # Finding missing rules
        missing = find_missing_rule(main_rule, dict_exc_no_main)
        # Missing rules already handle
        handle_exceptions = []
        # Add all missing rules
        while missing:
            # Get exceptions to handle, i.e. the deepest
            missing_rules = missing[max(missing, key=int)]
            # Handle the first one
            add_missing_rule(main_rule, dict_exc_no_main, missing_rules[0])
            # Indicate that it has been handle
            handle_exceptions.append(missing_rules[0])
            # Is there other exceptions?
            done = True
            # Scan all exceptions
            for mis in missing_rules:
                # Is there at least one not handle?
                if mis not in handle_exceptions:
                    done = False
            # There is more exceptions
            if not done:
                # Finding missing rules
                missing = find_missing_rule(main_rule, dict_exc_no_main)
            else:
                # We are done
                missing = None

    # Return all correct rules
    return correct_rules

# NOT TESTED DIRECTLY
def find_missing_rule(main_rule, dict_of_rule, depth=0):
    """Find all missing rules of an exception in a main rule

        :param main_rule: the main rule to search in
        :type main_rule: :py:class:`Rule`
        :param dict_of_rule: Raw rules of an exception
        :type dict_of_rule: Dict of pos/val
        :param depth: Depth of missing rule (default: `0`)
        :type depth: int

        :return: Missing rules and their positions and depth (key)
        :rtype: defaultdict(list)
    """

    # Dict of missing rules. Key is depth.
    ret = defaultdict(list)
    # For each rule of the exception
    for i in dict_of_rule:
        # Backup the dict
        dict_of_rule_small = dict_of_rule.copy()
        # Remove current rule
        dict_of_rule_small.pop(i)
        # Create a proper Rule from this rule
        tmp_rule = Rule(i, dict_of_rule[i], False, -1)
        # Is this Rule exist?
        founded = None
        # For all sub-rule of main_rule
        for j in main_rule.rules:
            if j.equ(tmp_rule):
                # the Rule exist, backup the 'proper' one
                founded = j
        # If the Rule exist, take the 'proper' one as main_rule
        if founded:
            # Search for remaining rules in sub-rules of current Rule
            tmp_ret = find_missing_rule(founded, dict_of_rule_small,
                                        depth + 1)
            # Update results
            ret.update(tmp_ret)
        # The Rule does not exist in current sub-rules
        else:
            # Add it to results
            ret[depth].append((i, dict_of_rule[i]))

    return ret

# NOT TESTED DIRECTLY
def add_missing_rule(main_rule, dict_of_rule, rule_to_add):
    """Add a rule of an exception in a main rule

        :param main_rule: the main rule to add in
        :type main_rule: :py:class:`Rule`
        :param dict_of_rule: Raw rules of an exception
        :type dict_of_rule: Dict of pos/val
        :param rule_to_add: The rule to add
        :type rule_to_add: Tuple(pos/val)
    """
    # Find reachable positions
    reachable_pos = find_rechable_pos(main_rule, dict_of_rule)
    # Smaller is deeper, add to deepest
    where_to_add = reachable_pos[min(reachable_pos)]
    # Create the Rule for this exception
    tmp_rule = Rule(rule_to_add[0], rule_to_add[1], False, -1)
    # Change upper rules to cut
    # Dangerous, works because .equ doesn't look cutting position.
    # I can't find an upper rule that should be at F with sub-rule at F
    # Something like '(D,)(G)': False, '(X)(D,)(G)': False
    # But it is none sens, but this actually BUG...
    # What I should do is checking if the rule already exist. If so, add
    # a new one. But I will end-up with two identical rules at the same
    # level saying T and F.
    where_to_add.cut = True
    # If it is not already there
    if not where_to_add.contains(tmp_rule) and not where_to_add.equ(tmp_rule):
        # Add manually the rule
        where_to_add.rules.append(tmp_rule)

# NOT TESTED DIRECTLY
def find_rechable_pos(main_rule, dict_of_rule):
    """Find all positions reachable on a main rule according to several
    rules.

        :param main_rule: the main rule to search in
        :type main_rule: :py:class:`Rule`
        :param dict_of_rule: Raw rules of an exception
        :type dict_of_rule: Dict of pos/val

        :return: Reachable :py:class:`Rule` and their depth (key)
        :rtype: dict()
    """
    ret = {}
    # We finish to parse all rules, we are as deeper as possible
    if not dict_of_rule:
        # This is a possibility
        ret[len(dict_of_rule)] = main_rule
    else:
        # For each rules
        for i in dict_of_rule:
            # Create the corresponding rule
            tmp_rule = Rule(i, dict_of_rule[i], False, -1)
            # Get the corresponding rule in main_rule
            new_main_rule = main_rule.contains(tmp_rule)
            # If it exist
            if new_main_rule:
                # Copy of the dict
                dict_of_rule_small = dict_of_rule.copy()
                # Remove from the dict the rule that exist in main_rule
                dict_of_rule_small.pop(i)
                # Search with the smaller dict and the new main_rule
                tmp_ret = find_rechable_pos(new_main_rule, dict_of_rule_small)
                # Update results
                ret.update(tmp_ret)
            # This rule does not exist in main_rule
            else:
                # Add main_rule to possibilities
                ret[len(dict_of_rule)] = main_rule
    return ret

def handle_rule(seq, pos, a_rule, cut):
    """Recursive handling of a :py:class:`Rule` determining if a
    sequence must be cutted at a given position according to the rule.

    :param seq: sequence to test
    :param pos: position on the sequence
    :param a_rule: the rule
    :param cut: boolean telling if it must be cutted or not
    :type seq: str
    :type pos: int
    :type a_rule: :py:class:`Rule`
    :type cut: bool

    :return: `True` if sequence must be cutted
    :rtype: bool or None
    """

    # return of the function: should we cut this?
    ret = cut
    # Need to try because it can be the first/last letter
    # and we need to look before/after
    # After is handle by try, but before, because python like str[-x],
    # we need an if :-/
    try:
        # If the rule applies, i.e. the letter to watch is the good one
        if (pos + a_rule.index) >= 0 and \
                seq[pos + a_rule.index] == a_rule.letter:
            # If no previous 'False' and this is cutting
            if a_rule.cut and ret is not False:
                ret = True
                # Handle the sub-rules (exceptions)
                for rul in a_rule.rules:
                    # Apply the rule: do we need to cut?
                    ret = handle_rule(seq, pos, rul, ret)
            # Is is not cutting
            elif not a_rule.cut:
                # Reinit
                ret = None
                # Handle sub-rules
                if a_rule.rules:
                    # Handle the rules (exceptions)
                    for rul in a_rule.rules:
                        # Apply the rule: do we need to cut?
                        ret = handle_rule(seq, pos, rul, ret)
                # No sub-rules and not cutting
                else:
                    # We are at the end a of rule that applies
                    # and say to NOT cut. So it will never cut.
                    ret = False
    # Doesn't work: begin or end of sequence, don't change cut value
    except IndexError:
        pass
    return ret

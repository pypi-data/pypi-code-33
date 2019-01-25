# -*- coding: utf-8 -*-
""" Generate the 'sim_db'/'sdb' command line tool.

The 'sim_db/sim_db/' directory is added to the PATH if wished, so that it can 
be run from anywhere. For Linux and Mac this involes adding a line to 
~/.bashrc and ~/.bash_profile respectfully, where for as Windows nothing is 
done.
"""
# Copyright (C) 2017-2019 Håkon Austlid Taskén <hakon.tasken@gmail.com>
# Licenced under the MIT License.

from commands import helpers
import fnmatch
from sys import platform
import sys
import os


def add_path_to_bash_file(where_to_add_path, sim_db_sim_db_dir):

    # Check if bash setting file exists
    if not os.path.isfile(where_to_add_path):
        answer = helpers.user_input(
                "{0} does not seem to exists. Would you "
                "like to add one? (y/n)\n (Recommended and needed to run "
                "the command line tool.)\n".format(where_to_add_path))
        if (answer == 'y' or answer == 'Y' or answer == 'yes'
                    or answer == 'Yes'):
            bash_file = open(where_to_add_path, 'w')
            bash_file.close()
        else:
            exit()

    # Check if path is already added
    bash_file = open(where_to_add_path, 'r')
    line_number = 0
    line_number_last_sim_db_path = -1
    for line in bash_file.readlines():
        line_number += 1
        if line.strip() == "# Add sim_db command line tool to PATH":
            line_number_header_sim_db_path = line_number
        if line.split(' ')[0] == 'export':
            if (len(line.split('/sim_db/sim_db')) == 2
                        and line.split('/sim_db/sim_db')[1].strip() == ""):
                line_number_last_sim_db_path = line_number
                prev_added_path = line.split(':')[-1].strip()
                prev_added_path = prev_added_path.rsplit('/', 1)[0]
                if prev_added_path == sim_db_sim_db_dir:
                    print("\nThe path to sim_db is already added to {0}."
                          .format(where_to_add_path))
                    return False

    # Add path
    answer = helpers.user_input(
            "\nWould you like to add "
            "'sim_db/sim_db' to your PATH in {0}? (y/n)\n"
            "(Recommended and needed to run command line tool.)\n"
            .format(where_to_add_path))
    if answer == 'y' or answer == 'Y' or answer == 'yes' or answer == 'Yes':
        if line_number_last_sim_db_path == -1:
            bash_file = open(where_to_add_path, 'a')
            bash_file.write("\n# Add sim_db command line tool to PATH\n")
            bash_file.write("export PATH=$PATH:{0}\n"
                            .format(sim_db_sim_db_dir))
            bash_file.close()
            print("\nRemember to source the newly added path:")
            print("$ source {0}".format(where_to_add_path))
        else:
            bash_file = open(where_to_add_path, 'r')
            bash_file_lines = bash_file.readlines()
            bash_file.close()
            bash_file = open(where_to_add_path, 'w')
            bash_file_lines.insert(
                    line_number_last_sim_db_path,
                    "export PATH=$PATH:{0}\n".format(sim_db_sim_db_dir))
            bash_file_lines = "".join(bash_file_lines)
            bash_file.write(bash_file_lines)
            bash_file.close()
            print("\nRemember to source the newly added path:")
            print("$ source {0}".format(where_to_add_path))
        return True
    else:
        print("No changes were made to {0}".format(where_to_add_path))
        return False


def main():
    sim_db_sim_db_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))

    where_to_add_path = None
    home = os.path.expanduser("~")
    if platform == "linux" or platform == "linux2" or platform == "linux3":
        where_to_add_path = "{0}/.bashrc".format(home)
    elif platform == "darwin":
        where_to_add_path = "{0}/.bash_profile".format(home)
    elif platform == 'cygwin':
        where_to_add_path = "{0}/.bashrc".format(home)

    if where_to_add_path:
        add_path_to_bash_file(where_to_add_path,
                              sim_db_sim_db_dir.replace(" ", "\ "))

    if os.sep == '/':
        sim_db_sim_db_dir = sim_db_sim_db_dir.replace(" ", "\ ")
    for program in ['sim_db', 'sdb', 'sim_db_cd.sh']:
        os.system("chmod u+x {0}".format(
                os.path.join(sim_db_sim_db_dir, program)))


if __name__ == '__main__':
    main()

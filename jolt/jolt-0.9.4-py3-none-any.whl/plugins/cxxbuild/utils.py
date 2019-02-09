##############################################################################
#
# (C) 2016 - Robert Andersson - All rights reserved.
#
# This file and its contents are the property of Robert Andersson
# and may not be distributed, copied, or disclosed, in whole or in part,
# for any reason without written consent of the copyright holder.
#
##############################################################################


import sys
import os
import imp


class DepfileParser:
    def __init__(self, filename):
        self.data = ""
        self.product = ""
        self.dependencies = []

        if not os.path.exists(filename):
            return

        with open(filename) as f:
            self.data = f.read()

        self.data = self.data.replace("\n", "")
        self.data = self.data.replace("\r", "")
        self.data = self.data.replace("\\", "")

        index = self.data.find(":")
        if index < 0:
            return

        self.data = self.data[index+1:]
        self.product = self.data[0:index]
        self.dependencies = [dep for dep in self.data.split(" ") if dep]
        self.dependencies = [os.path.normpath(dep) for dep in self.dependencies]

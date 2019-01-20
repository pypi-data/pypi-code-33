# The contents of this file are subject to the Mozilla Public License
# Version 1.1 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
# http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"
# basis, WITHOUT WARRANTY OF ANY KIND, either express or implied. See the
# License for the specific language governing rights and limitations
# under the License.
#
# The Original Code is "Simplenlg".
#
# The Initial Developer of the Original Code is Ehud Reiter, Albert Gatt and Dave Westwater.
# Portions created by Ehud Reiter, Albert Gatt and Dave Westwater are
# Copyright (C) 2010-11 The University of Aberdeen. All Rights Reserved.
#
# Contributor(s): Ehud Reiter, Albert Gatt, Dave Wewstwater, Roman Kutlak, Margaret Mitchell.

from enum import Enum

# An enumeration representing the different types of temporal sense that can be
# applied to a verb.
class Tense(Enum):
    # The action described by the verb will happen in the future. For example,
    # John will kiss Mary, the dog will eat a bone.
    FUTURE = 0
    # The action described by the verb happened in the past. For example,
    # John kissed Mary, the dog ate a bone.
    PAST = 1
    # The action described by the verb is happening in the present time. For
    # example, John kisses Mary, the dog eats a bone.
    PRESENT = 2

    def __str__(self):
        return self.name

# /usr/bin/env python

# This file is part of pyspring.

# pyspring is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# pyspring is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with pyspring.  If not, see <http://www.gnu.org/licenses/>.


def is_palindrome(number):
    number = str(number)
    number_middle = len(number) // 2  # Integer rather than float
    # `reversed` converts to a list
    if number[:number_middle] == ''.join(reversed(number[-number_middle:])):
        return True
    return False


def partial_palindrome(number, palindrome_digits):
    if is_palindrome(str(number)[-palindrome_digits:]):
        return True
    return False

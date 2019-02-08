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

from statistics import mean


def right_justify(sentence, length):
    current_length = len(sentence)
    return ' '*(length-current_length) + sentence


def sum_to(length, is_even):
    total_numbers = []
    for counter in range(1, length + 1):
        if (is_even and counter % 2 == 0) or (not is_even and counter % 2 == 1):
            total_numbers.append(counter)
    return sum(total_numbers)


def is_right_angled(*lengths):
    lengths = sorted(lengths)
    if lengths[0] ** 2 + lengths[1] ** 2 == lengths[2] ** 2:
        return True
    return False


def draw_grid(square_width, square_height):
    start_line = ('*---' * square_width) + '*'
    middle_line = ('|   ' * square_width) + '|'

    for total_counter in range(0, square_height):
        print(start_line)
        print(middle_line)
        print(middle_line)
    print(start_line)


def user_summarise():
    position_number = 1
    number_list = []
    while True:
        current_number = float(input('Enter number no.{}: '.format(position_number)))
        if current_number < 0:
            print('')
            print('Maximum number:', max(number_list))
            print('Minimum number:', min(number_list))
            print('Mean:', mean(number_list))
            return
        number_list.append(current_number)
        position_number += 1


def is_sorted(user_list):
    if sorted(user_list) == user_list:
        return True
    return False

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

from random import randint
total_guesses = 0


def user_guesser(mode, length, number):
    user_number = str(input('Enter a {0} digit number: '.format(length)))
    global total_guesses
    total_guesses += 1
    correct_positions = []
    for char_pos in range(0, length):
        if user_number[char_pos] == number[char_pos]:
            correct_positions.append(str(char_pos + 1))
    if len(correct_positions) == length:
        print('Congratulations, you won in {0} guesses!'.format(total_guesses))
        return
    if mode == 'easy':
        print('')
        print('Incorrect')
        if not correct_positions:
            print('No correct positions\n')
        else:
            print('Correct positions:', ' '.join(correct_positions) + '\n')
        user_guesser('easy', 4, number)
    elif mode == 'normal':
        print('')
        print('Incorrect\n')
        user_guesser('normal', 4, number)
    else:
        print('')
        print('Incorrect\n')
        user_guesser('hard', 5, number)


if __name__ == '__main__':
    user_lengths = {'hard': 5, 'normal': 4, 'easy': 4}
    user_mode = input('Enter a mode (Easy/Normal/Hard): ').lower()
    if user_mode == 'hard':
        computer_number = str(randint(10000, 99999))
    else:
        computer_number = str(randint(1000, 9999))
    user_guesser(user_mode, user_lengths[user_mode], computer_number)

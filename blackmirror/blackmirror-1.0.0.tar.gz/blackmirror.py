#!/usr/bin/env python
import argparse
import curses
import curses.textpad
import random
import sys
import time
import webbrowser
from enum import Enum

__version__ = '1.0.0'

parser = argparse.ArgumentParser(
    prog='blackmirror',
    description='Look into the black mirror...',
)
subparsers = parser.add_subparsers()
bandersnatch_parser = subparsers.add_parser(
    'bandersnatch',
    description='Confront the bandersnatch!',
)
bandersnatch_parser.set_defaults(command='bandersnatch_command')


def main():
    if len(sys.argv) <= 1:
        parser.print_help()
        sys.exit(1)
    parsed = parser.parse_args(sys.argv[1:])
    globals()[parsed.command]()


def bandersnatch_command():
    choice = curses.wrapper(curses_choice, left_label='Learn More', right_label='Watch Trailer')
    if choice == Choice.LEFT:
        webbrowser.open('https://en.wikipedia.org/wiki/Black_Mirror:_Bandersnatch')
    elif choice == Choice.RIGHT:
        webbrowser.open('https://www.youtube.com/watch?v=XM0xWpBYlNM')


class Choice(Enum):
    NOTHING = 1
    LEFT = 2
    RIGHT = 3


class Coloring(Enum):
    CYAN = 1
    YELLOW = 2


def curses_choice(stdscr, left_label, right_label):
    curses.init_pair(Coloring.CYAN.value, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(Coloring.YELLOW.value, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    stdscr.timeout(100)
    curses.curs_set(0)  # Make cursor invisible
    start = time.time()
    choice = Choice.NOTHING
    choice_time = 10.0
    while True:
        elapsed = time.time() - start
        if elapsed > choice_time:
            break

        # Choice
        char = stdscr.getch()
        if char == curses.KEY_LEFT:
            choice = Choice.LEFT
        elif char == curses.KEY_RIGHT:
            choice = Choice.RIGHT
        elif char == ord('\n') and choice != Choice.NOTHING:
            break
        elif char == ord('q'):
            # Quit
            break

        if elapsed > 8.0 and choice == Choice.NOTHING:
            choice = random.choice([Choice.LEFT, Choice.RIGHT])

        # Draw
        height, width = stdscr.getmaxyx()
        choice_left_width = width // 2
        choices_height = max(3, int(0.3 * height))
        choices_y_start = height - choices_height
        stdscr.erase()

        stdscr.addstr(0, 0, 'Make Your Choice! Press left or right then enter.')

        draw_bandersnatch(
            stdscr,
            1,
            0,
            choices_y_start - 2,
            width - 1,
        )

        stdscr.addstr(choices_y_start - 1, 0, get_time_bar(elapsed, choice_time, width))

        curses.textpad.rectangle(stdscr, choices_y_start, 0, height - 1, choice_left_width)
        stdscr.addstr(
            choices_y_start + choices_height // 2,
            1 + (choice_left_width - len(left_label)) // 2,
            left_label,
            (curses.A_REVERSE if choice == Choice.LEFT else 0),
        )

        curses.textpad.rectangle(stdscr, choices_y_start, choice_left_width + 1, height - 1, width - 2)
        stdscr.addstr(
            choices_y_start + choices_height // 2,
            1 + choice_left_width + (choice_left_width - len(right_label)) // 2,
            right_label,
            (curses.A_REVERSE if choice == Choice.RIGHT else 0),
        )

        stdscr.refresh()

    return choice


def draw_bandersnatch(stdscr, top_y, left_x, bottom_y, right_x):
    real_left_x = (right_x - left_x - 102) // 2

    y_offset = 0
    x_offset = 0
    for char in bandersnatch:
        if char == '\n':
            y_offset += 1
            x_offset = 0
            continue
        elif char in 'CY':
            y = top_y + y_offset
            x = real_left_x + x_offset
            if top_y <= y <= bottom_y and left_x <= x <= right_x:
                stdscr.addstr(
                    y,
                    x,
                    '█',
                    curses.color_pair(Coloring.CYAN.value if char == 'C' else Coloring.YELLOW.value),
                )
        x_offset += 1


bandersnatch = '''\
                            CC          CC  CC      CC      CC  CC        CCCCCCCCCC
                            CC          CC    CC    CC          CC    CCCC          CCCC
              CCCCCCCC        CCCC                              CC  CC
                      CC        CC                        CCCC      CC      CCCCCC
                        CC                CCCCCC      CCCCCCCC            CC
      CCCCCCCCCCCC        CCCC      CCCCCCCCCCCC  CCCCCCCCCCCCCC      CCCC        CCCCCCCCCCCC
      CCCCCCCCCCCCCCCC              CCCCCCCCCCCC  CCCCCCCCCCCCCCCC                CCCCCCCCCCCC
        CCCC  CCCCCCCC          CCCCCCCCCCCCCCCC  CCCCCCCCCCCCCCCC            CCCCCCCC  CCCC
        CCCC      CCCC          CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC            CCCC      CCCC
        CCCC        CC          CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC          CC      CCCCCC
        CCCCCCCC                CCCCCCCCCC    CC    CCCCCCCCCCCC                    CCCCCC
            CCCCCCCC            CCCCCCCCCCCCCCCC    CCCCCCCCCCCCCCCC            CCCCCC        CC
    CC          CCCC          CC          CCCCCC    CCCCCC                      CCCC          CC
    CC                                YY        CCCC    CC  YY                                CC
    CC  CC    CC                    YY  YY    CCCCCCCC    YY  YY                        CC
    CC  CC    CC                    YYYY                    YYYY
  CC    CC    CC              CCCC            CCCCCCCC            CCCCCC          CC  CC
  CC    CC    CC          CCCCCCCCCCCCCCCCCC  CCCCCCCC  CCCCCCCCCCCCCCCC        CC    CC      CC
  CC          CC        CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC    CCCCCCCC      CC    CC        CC
CC            CC                  CC    CC  CCCCCCCCCCCC  CC  CCCCCC            CC    CC        CC
CC            CC                        CCCC            CCCC                          CC    CC  CC
CC      CC    CC                      CCCCCCCC        CCCCCCCC                        CC    CC  CC
CC    CC    CC    CC              CC  CCCCCCCCCC    CCCCCC  CC  CC              CC      CC  CC    CC
      CC    CC    CC              CC  CC  CCCCCCCCCCCCCCCC  CC  CC              CC      CC  CC    CC
      CC          CC    CC        CC                            CC              CC      CC  CC    CC
      CC          CC    CC        CC      YY    YYYY    YY      CC              CC      CC  CC    CC
  CC  CC        CC      CC                    YY    YY          CC                CC    CC        CC
  CC  CC        CC      CC                YY    YYYY    YY                CC      CC    CC        CC
  CC  CC        CC      CC                                    CC            CC    CC    CC  CC    CC
  CC  CC        CC      CC            CC  CCCCCCCCCCCCCCCC    CC            CC    CC    CC  CC      CC
  CC  CC    CC  CC      CC            CC  CCCC  CC    CCCC  CCCC                  CC    CC          CC
  CC        CC  CC      CC                CCCC        CCCC  CC                    CC    CC          CC
  CC      CC          CC                  CCCC  CCCC  CCCC                  CC            CC        CC
  CC      CC          CC                  CCCC        CCCC                  CC            CC        CC
  CC      CC                              CCCC        CCCC                  CC            CC        CC
  CC      CC                              CC            CC                  CC            CC        CC'''


def get_time_bar(elapsed, choice_time, width):
    percent_elapsed = elapsed / choice_time
    percent_not_elapsed = 1.0 - percent_elapsed
    half_width = width // 2
    return (
        ' ' * int(percent_elapsed * half_width) +
        '█' * int(percent_not_elapsed * half_width) +
        ('' if width % 2 == 0 else '█') +
        '█' * int(percent_not_elapsed * half_width) +
        ' ' * int(percent_elapsed * half_width)
    )


if __name__ == '__main__':
    main()

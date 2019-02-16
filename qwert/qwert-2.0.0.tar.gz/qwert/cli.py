#!/usr/bin/env python
# encoding: utf-8


def raw(s: str = ''):
    """
    Get input, if empty retry.

    :param str s: prompt
    :return: str
    """
    while True:
        value = input('> {}: '.format(s))
        if value:
            return value


def confirm(s: str = ''):
    """
    Ask yes/no, if invalid retry.

    :param str s: prompt
    :return: bool
    """
    while True:
        value = input('> {} [y/n]: '.format(s)).lower()
        if value:
            if value in 'yesrtui':
                return True
            elif value in 'novbm,':
                return False


def pause(s: str = 'press any key to continue'):
    """
    Pause with a prompt.

    :param str s: prompt
    :return: None
    """
    _ = input('# {}: '.format(s))
    return


def copy(value: str, with_prompt: bool = True):
    """
    Copy to clip.

    :param str value: value to be copied
    :param bool with_prompt: prompt and pause
    :return: None
    """
    import cli_print as cp
    import pyperclip

    if with_prompt:
        pause('Press any key to copy ' + cp.Fore.LIGHTCYAN_EX + value + cp.Style.RESET_ALL + ' to clip')
        cp.wr('\x1b[1A\x1b[2K')  # remove the prompt line.
        cp.fi()
    cp.about_t('Copy', value, 'to clip')
    pyperclip.copy(value)
    cp.success()
    return

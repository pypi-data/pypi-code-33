"""
Parsing utilities for slack_invoker
"""

import shlex

class ParseError(Exception):
    """
    Signifies an exception parsing arguments to a slack_invoker invocation target.
    """
    pass

def wrap_runner(parser, runner):
    """
    Wraps a function so that it can accept inputs as they would be provided to an
    argparse argument parser.

    Args:
    1. parser - an argparse argument parser
    2. runner - function whose arguments correspond (in name) to the arguments parsed by parser

    Returns:
    Function which accepts a string or an array of strings, parses them, and passes the
    corresponding namespace as keyword arguments to runner
    """
    def wrapped_runner(raw_args=''):
        tokenized_args = raw_args
        if raw_args == str(raw_args):
            tokenized_args = shlex.split(raw_args)

        if '-h' in tokenized_args or '--help' in tokenized_args:
            return '```{}```'.format(parser.format_help())

        try:
            args = parser.parse_args(tokenized_args)
        except SystemExit as e:
            raise ParseError('ERROR: Could not parse raw_args={}, exited with code={}'.format(
                raw_args,
                str(e)
            ))
        kwargs = vars(args)
        return runner(**kwargs)

    return wrapped_runner

def slack_email(raw_email):
    """
    Extracts e-mail address from a slack e-mail link

    Args:
    1. raw_email - Slack email string (of the form '<mailto:{email}|{email text}>')

    Returns:
    Email address from slack email string (the {email} bit in the template above)
    """
    raw_email_string = str(raw_email)
    email_section = raw_email.split('|')[0]
    if not email_section:
        raise IOError('No email found in {}'.format(raw_email_string))
    MAILTO = '<mailto:'
    if email_section[:len(MAILTO)] != MAILTO:
        raise IOError('{} prefix not found in email section of {}'.format(MAILTO, email_section))
    email = email_section[len(MAILTO):]
    return email

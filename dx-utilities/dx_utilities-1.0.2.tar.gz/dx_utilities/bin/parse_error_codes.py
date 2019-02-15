"""Parse coded-errors handled in the codebase.

Usage::

    git grep -WE "raise \w{10,}\(" | python -m bin.parse_error_codes

Prints in standard output pairs of the form::

    <error-code> <parent function or class>

"""
import logging
import argparse

import sys
import re

def md_icode(text):
    """Transform to markdown inline code.

    :param str text: The text to transform.
    :rtype: str
    """
    return '`%s`' % text

def main():
    logging.info("Parsing error codes...")
    file_reg = re.compile(r'dx_.+?\.py')
    class_reg = re.compile(r'class\s(?P<fname>\w+)\(')
    func_reg = re.compile(r'def\s(?P<fname>\w+)\(')
    raise_reg = re.compile(r'raise [a-z]{10,}\((?P<code>\d{4}\b)?',
                           flags=re.I)
    error_reg = re.compile(r'(?P<code>\d{4}\b)')

    funcs = []
    classes = []
    parsed = []
    header = []
    header.append(('', 'Error code', 'Source file', 'Object reference', ''))
    header.append(('', 10*'-', 10*'-', 10*'-', ''))
    while True:
        try:
            line = next(sys.stdin)
        except StopIteration:
            break
        cmatch = class_reg.search(line)
        if cmatch:
            classes.append(cmatch.group('fname'))
            continue
        fmatch = func_reg.search(line)
        if fmatch:
            funcs.append(fmatch.group('fname'))
            continue
        rmatch = raise_reg.search(line)
        if rmatch:
            mname = file_reg.search(line).group()
            if rmatch.group('code'):
                try:
                    cname = ''
                    if classes:
                        cname = classes[-1]
                    fname = funcs[-1]
                    name = '.'.join((cname, fname)) if cname else fname
                except:
                    print(repr(funcs))
                    raise
                else:
                    pout = ['']
                    pout.extend(map(md_icode, (rmatch.group('code'), mname, name)))
                    pout.append('')
                    parsed.append(pout)
                    continue
            else:
                try:
                    line = next(sys.stdin)
                except StopIteration:
                    break
                code = error_reg.search(line).group('code')
                try:
                    cname = ''
                    if classes:
                        cname = classes[-1]
                    fname = funcs[-1]
                    name = '.'.join((cname, fname)) if cname else fname
                except:
                    print(repr(funcs))
                    raise
                else:
                    pout = ['']
                    pout.extend(map(md_icode, (code, mname, name)))
                    pout.append('')
                    parsed.append(pout)
                continue
    parsed.sort(key=lambda t: t[1])
    parsed = header + parsed
    print('\n'.join(['|  '.join(t) for t in parsed]))


if __name__ == "__main__":
    main()

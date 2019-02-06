# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Copyright 2019 Daniel Mark Gass, see __about__.py for license information.
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

from textwrap import wrap


def wrap_message(exc):
    lines_out = []
    queue = []
    for line in str(exc).split('\n'):
        stripped_line = line.strip()
        if not stripped_line or (stripped_line[0] in '+|'):
            lines_out.extend(wrap('\n'.join(queue)))
            lines_out.append(line)
            queue = []
        else:
            queue.append(line)

    if queue:
        lines_out.extend(wrap('\n'.join(queue)))

    return '\n'.join(lines_out)


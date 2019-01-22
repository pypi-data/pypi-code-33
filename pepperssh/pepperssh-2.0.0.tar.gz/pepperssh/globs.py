
# Implementation of globbing for the archive function.
#
# This is almost the same as fnmatch.translate but handles '**'.  The built-in glob module
# does support it, but manually instead of a more advanced regular expression.
# For now we'll have to reimplement.

import re


NAMECHARS = r'[^/]'


def translate_pattern(pattern):
    """
    Convert a glob pattern, including support for '**', to a regular expression.
    """

    # The only double-asterisk patterns we allow are:
    #
    # - **/test.log - matches in any directory including root.  This is the same
    #   as just "test.log", so the easiest thing to do is to delete it.
    #
    # - /**/test.log - Same as above, so delete.
    #
    # - a/**/test.log - Match 'a', then any file named test.log below including
    #   "a/test.log".  A leading slash is irrelevant here.
    #
    # - a/** - match everything under a, including files in subdirectories.

    parts = []

    if pattern.startswith('/'):
        # This means it matches starting at the root directory.  Since we're
        # going to match against a string that starts under the root
        # directory, we'll replace it with "^".
        pattern = pattern[1:]
        parts.append(r'^')
    else:
        parts.append('(^|/)')

    if pattern.endswith('/'):
        # This just means the user is trying to exclude an entire directory.
        # Since we match against files, exclude everything from their down.
        pattern += '*'

    # Collapse repeated double stars which have no meaning.
    pattern = re.sub(r'\*{2}(/\*{2})+', '**', pattern)

    # Leading double starts don't many anything either, so remove those.
    #  pattern = re.sub(r'^ (\*{2} /)+', '([^/]+/)?', pattern, flags=re.VERBOSE)
    if pattern.startswith('**/'):
        parts.append('([^/]+/)*')
        pattern = pattern[3:]

    components = pattern.split('/')

    # I need to know if is the first or last component, so I'll use an index.
    for idx, comp in enumerate(components):
        isfirst = (idx == 0)
        islast  = (idx == len(components) - 1)

        if comp == '**':
            assert not isfirst
            if islast:
                # We're only going to match against files, so we can match
                # anything from here down.  But it must match *something*, so
                # use '+'.
                parts.append('.+')
            else:
                # A double-star in the middle matches *zero* or more
                # subdirectories.  The zero is what complicated this entire
                # function.  We can match nothing, but we must have a slash
                # afterwards.  Note that this will match invalid names like
                # "//a", but since are matching against real paths it is not an
                # issue.
                parts.append('([^/]+/)*')
        else:
            # This is a directory or filename component.
            parts.append(_translate_component(comp))
            if not islast:
                parts.append('/')
            else:
                parts.append('$')

    return re.compile(''.join(parts))


def _translate_component(pattern):
    """
    Translates a pattern for a single path component, which is a filename or a
    directory name.
    """
    # We need to escape everything except '?' and '*'.  I can't see an easy
    # way to do so that doesn't introduce other problems, so I'll simply
    # split on them.  We'll use capturing parens to ensure we get the text
    # between them, and the special characters themselves.
    #
    # Note that this causes empty entries at the beginning and end if they
    # start with special characters: *.log => ['', '*', '.log].  They can be
    # discarded.
    #
    # We accept multiple wildcards like '?*?'.  This example is silly, but
    # since '*' technically means "zero or more', '?*' could be useful.  We
    # simply require the wildcard match to have at least a character for
    # each '?', so "?***?***" is just 2 or more characters.

    result = []

    parts = re.split(r'([?*]+)', pattern)

    for part in parts:
        if not part:
            continue

        if '*' in part or '?' in part:

            # Definitely a wildcard, so start with the wilcard characters.  Then
            # we'll append items to determine the number of these allowed.

            # NB: At one point I had complex code to generate a more readable
            # regular expression, such as "X+" instead of "X{1,1}".  Since this
            # isn't really for human consumption I've simplified to always use
            # {min,max}.

            question_marks = part.count('?')
            minchars = str(question_marks)
            maxchars = ('' if '*' in part else minchars)

            exp = '%s{%s,%s}' % (NAMECHARS, minchars, maxchars)

            result.append(exp)
        else:
            # A text portion.  Escape it in case it has special regexp characters.
            result.append(re.escape(part))

    return ''.join(result)

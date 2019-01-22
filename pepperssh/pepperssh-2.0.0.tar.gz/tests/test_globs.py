# pytest tests for the wildcard matching in archive globs.

# Use python -m pytest from the root directory.


from pepperssh.globs import translate_pattern

def _match(regexp, filenames):
    r = translate_pattern(regexp)

    filenames = [fn.strip() for fn in filenames.strip().split('\n') if fn.strip()]

    for fn in filenames:
        assert r.search(fn), f'No match: {regexp} {fn!r}'


def _dont_match(regexp, filenames):
    r = translate_pattern(regexp)

    filenames = [fn.strip() for fn in filenames.strip().split('\n') if fn.strip()]

    for fn in filenames:
        assert r.search(fn) is None, f'Invalid match: {regexp} {fn!r}'


def test_leading_double():

    _match('**/b',
           """
           b
           x/b
           x/y/z/b
           """)

    _dont_match('**/b',
                """
                ab
                x/ab
                a/b/c
                b/c
                """)

    # Since a double-star includes subdirectories, repeating it has no effect.  We allow it
    # but treat it as if it were a single: 'a/**/**/**/b' => 'a/**/b'
    _match('**/**/b',
           """
           b
           x/b
           x/y/z/b
           """)

    _dont_match('**/**/b',
                """
                ab
                x/ab
                a/b/c
                b/c
                """)


def test_filename():
    # Just a filename should match the file anywhere.
    _match('b',
           """
           b
           x/b
           x/y/z/b
           """)

    _dont_match('b',
                """
                ab
                x/ab
                b/a
                """)


def test_filename_wildcard():
    # Just a pattern with no slashes or double stars should match a filename in any
    # directory.

    _match('*.log',
           """
           .log
           test.log
           a/b/c/test.log
           """)

    _dont_match('*.log',
                """
                test.txt
                """)


def test_subdir_wildcard():
    _match('a*b/test.log',
           """
           ab/test.log
           axb/test.log
           x/y/ab/test.log
           x/axyzb/test.log
           """)

    # The star does not match '/'.  It only matches a single directory.
    _dont_match('a*b/test.log',
                """
                a/b/test.log
                ax/b/test.log
                """)


def test_trailing_star():
    # When a star is trailing, it can match any file in the previously named directory.
    _match('a/*',
           """
           a/x
           x/y/a/z
           """)

    _dont_match('a/*',
                """
                a
                x/a
                a/b/c
                """)


def test_question_star():
    "Mixing question marks and stars creates minimum length wildcards"
    # Mixing question marks and stars can be used to create a wildcard with a minimum number of
    # characters: ???* is a 3+ character wildcard.  If you mix in more stars, we ignore them
    # since they always match "zero or more".

    _match("?*.log",
           """
           test.log
           t.log
           a/b/c/t.log
           """)

    _dont_match("?*.log",
                """
                .log
                test.txt
                """)


def test_question():
    "A question mark matches a single character"
    _match("t?.log",
           """
           t1.log
           a/b/c/t1.log
           """)

    _dont_match("t?.log",
                """
                t12.log
                a/b/c/t12.log
                """)

def test_leading_slash():
    "A leading slash matches at the root"
    _match("/*.log",
           """
           .log
           test.log
           """)

    _dont_match("/*.log",
                """
                x/test.log
                x/y/z/test.log
                """)

    _match("/a/b/c/*.log",
           """
           a/b/c/.log
           a/b/c/test.log
           """)

    _dont_match("/a/b/c/*.log",
                """
                .log
                test.log
                a/b/test.log
                """)


def test_trailing_double_stars():
    """
    Trailing double-stars mean anything below matches.
    """
    _match("a/**",
           """
           a/test.log
           a/b/c/test.log
           b/c/a/test.log
           """)

    _match("/a/**",
           """
           a/test.log
           a/b/c/test.log
           """)

    _dont_match("a/**",
                """
                test.log
                x/z/y/test.log
                """)

    _dont_match("/a/**",
                """
                b/c/a/test.log
                """)

def test_directory_double_stars():
    "Double stars in middle match zero or more directories"
    _match("a/**/b",
           """
           a/b
           a/c/b
           a/c/d/b
           a/b/b
           x/y/a/b
           x/y/a/z/b
           """)

    _dont_match("a/**/b",
                """
                a/b/c
                ab
                """)

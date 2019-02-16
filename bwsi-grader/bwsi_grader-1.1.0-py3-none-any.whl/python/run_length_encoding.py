"""
# Run-Length Encoding
Run-length encoding is a simple method for compressing data that contains long sequences of repeated characters.

In this compression algorithm:
1. A standalone character will be unchanged. E.g `"a"` $\rightarrow$ `["a"]`.
2. A run of a character, `c`, repeated `N` times will be compressed to `["c", "c", N]`. E.g. `"bbbb"` $\rightarrow$ `['b', 'b', 4]`.

These two rules are all that you need to perform run-length encoding.

Let's look at a few examples of run-length-encoding:

- `"abcd"` $\rightarrow$ `['a', 'b', 'c', 'd']`
- `"abbbba"` $\rightarrow$ `['a', 'b', 'b', 4, 'a']`
- `"aaaabbcccd"` $\rightarrow$ `['a', 'a', 4, 'b', 'b', 2, 'c', 'c', 3, 'd']`
- `""` $\rightarrow$ `[]`
- `"1"` $\rightarrow$ `["1"]`

The decompression algorithm, run-length decoding, simply reverses this process:

- `['q', 'a', 'a', 4, 'b', 'b', 2, 'c', 'c', 3, 'd']` $\rightarrow$ `'qaaaabbcccd'`

Here, you will implement a run-length encoding and decoding algorithms. As indicated above, the run-length encoding algorithm should be able to accept a string and return a list with the appropriate string/integer entries, according to the encoding. The decoding algorithm need be able to accept a list with an encoded sequence, and return the decoded string.

You should be able to test both of your algorithms by feeding them into one another:
```python
>>> decoder(encoder("Wooooow!!!!! I'm totally getting compressed"))
"Wooooow!!!!! I'm totally getting compressed"
```

## Required Concepts
Sequence Types
- strings
- lists
- indexing & slicing

Conditional Statements
- basic if/else conditional blocks

For-Loops
- basic for-loops

Generators & Comprehensions
- the `range` generator

Basics of Functions
- the return statement
- basic function arguments


## Examples
```python
>>> encoder("abbbba")
['a', 'b', 'b', 4, 'a']

>>> decoder(['a', 'b', 'b', 4, 'a'])
'abbbba'
```

"""

from typing import Callable, Union, Iterable, Generator, List


__seed__ = ["runlengthencoding", "runlengthdecoding"]


def _gen_run(num_runs: int = 16) -> str:
    """generate random runs of characters"""
    import string
    from random import choices, randint
    chars = string.ascii_letters + string.digits + " "
    return "".join(i*randint(0, 4) for i in choices(chars, k=num_runs))


def _gen_encoded_seq() -> List[str]:
    """ randomly generates a encoded sequence"""
    import random
    import string

    def get_char(prev):
        if prev is not None:
            return ''.join(set(string.ascii_letters) - set(prev))
        else:
            return string.ascii_letters

    def single(prev): return [random.choice(get_char(prev))]

    def multi(prev):
        letter = random.choice(get_char(prev))
        number = random.randint(2, 5)
        return [letter, letter, number]

    seq = []
    prev = None
    for i in range(random.randint(0, 5)):
        item = random.choice([single, multi])(prev)
        seq.extend(item)
        prev = item[0]
    return seq


def encoder_grader(student_func: Callable[[str], List[Union[str, int]]]):
    """ Tests the student's run-length-encoding compressor.

    Parameters
    ----------
    student_func: Callable[[str], List[Union[str, int]]]
       The student's solution function.
    """
    from bwsi_grader import compare_functions
    from bwsi_grader.print import print_passed
    from hashlib import sha224

    def run_len_compr(it: Iterable) -> Generator:
        """ Generates run-length compression on an iterable of comparable items

            Parameters
            ----------
            it : Iterable[Any]
                An iterable of mutually comparable items

            Yields
            ------
            Any
                The next character in the compressed sequence."""

        iterable = iter(it)
        cnt = 0
        prev_item, item = None, None
        try:
            item = next(iterable)
            cnt = 1
            while True:
                prev_item = item
                item = next(iterable)
                if prev_item != item:
                    if cnt > 1:
                        yield from (prev_item, prev_item, cnt)
                    elif cnt == 1:
                        yield prev_item
                    cnt = 1
                else:
                    cnt += 1
        except StopIteration:
            if item is None or prev_item != item:
                pass
            elif cnt > 1:
                yield from (prev_item, prev_item, cnt)
            elif cnt == 1:
                yield item

    def compression_soln(in_string: str) -> List[Union[str, int]]:
        """
        Examples
        --------
        >>> compression_soln("aaabbacccc")
        ['a', 'a', 3, 'b', 'b', 2, 'a', 'c', 4]
        """
        return list(run_len_compr(in_string))

    for input_ in ("abcd", "ababa", "aabbaba", "abbbbaa", "aaaabbcccd", "", "2", "Hello Worldddd!!!"):
        compare_functions(student=student_func, soln=compression_soln, fn_args=(input_,))

    for i in range(1000):
        compare_functions(student=student_func, soln=compression_soln, fn_args=(_gen_run(),))

    print_passed(sha224(str.encode(__seed__[0])).hexdigest())


def decoder_grader(student_func: Callable[[List[Union[str, int]]], str]):
    """ Tests the student's run-length-decoding compressor.

    Parameters
    ----------
    student_func: Callable[[List[Union[str, int]]], str]
       The student's solution function.
    """
    from bwsi_grader import compare_functions
    from bwsi_grader.print import print_passed
    from hashlib import sha224

    def run_len_decompr(compr):
        """ Generates run-length decompression.

            Parameters
            ----------
            compr : Iterable[Any]
                An iterable of items and counts in a compressed sequence.

            Yields
            ------
            Any
                The next item in the decompressed sequence.

            Examples
            --------
            >>> run_len_decompr("aa3bb2acc4")
            <generator object run_len_decompr at 0x0000022FA63B6FC0>
            # will generate "a".. "a".. "a".. "b".. "b".. "a".. "c".. "c".. "c".. "c"..
            """
        compr = iter(compr)
        prev_char = None

        while True:
            try:
                char = next(compr)
                if char is not prev_char:
                    yield char
                    prev_char = char
                else:
                    cnt = int(next(compr))
                    prev_char = None
                    yield from (char for i in range(cnt - 1))
            except StopIteration:
                break

    def decompression_soln(in_list: List[Union[str, int]]) -> str:
        """
        Examples
        --------
        >>> decompression_soln(['a', 'a', 3, 'b', 'b', 2, 'a', 'c', 'c', 4])
        'aaabbacccc'
        """
        return "".join(run_len_decompr(in_list))



    # check some standard cases
    std_cases = [['a', 'b', 'c', 'd'],
                 ['a', 'b', 'a', 'b', 'a'],
                 ['a', 'a', 2, 'b', 'b', 2, 'a', 'b', 'a'],
                 ['a', 'b', 'b', 4, 'a', 'a', 2],
                 ['a', 'a', 4, 'b', 'b', 2, 'c', 'c', 3, 'd'],
                 [],
                 ['2'],
                 ['H', 'e', 'l', 'l', 2, 'o', ' ', 'W', 'o',
                  'r', 'l', 'd', 'd', 4, '!', '!', 3]]

    for input_ in std_cases:
        compare_functions(student=student_func, soln=decompression_soln, fn_args=(input_,))

    for i in range(1000):
        compare_functions(student=student_func, soln=decompression_soln, fn_args=(_gen_encoded_seq(),))

    print_passed(sha224(str.encode(__seed__[1])).hexdigest())

from __future__ import annotations

import inspect
from ast import literal_eval
from typing import Tuple, Dict, List, Union, Callable, TYPE_CHECKING
from warnings import warn

# noinspection PyPackageRequirements
from lark import Token, v_args

from jsom.jsomwarnings import TrailingCommaInArray, TrailingCommaInObject, \
    SingleQuotedString, UnquotedString, EmptyObjectValue

if TYPE_CHECKING:
    from jsom.parser import JsomParser

JsomValue = Union[
    List['JsomValue'],
    Dict[str, 'JsomValue'],
    float, int,
    bool,
    None
]

# There is some ugliness going on in here with all the getter methods and
# `inspect`, and you might be wondering "why?".
#
# As for `inspect`, if we have a list like this: [1, 2], it will get parsed as::
#
#    array
#      number	1
#      number	2
#
# Which means that Lark will:
#
# 1. First, call `number(Token(NUMBER, '1'))`, returning int(1).
#
# 2. Second, call `number(Token(NUMBER, '2'))`, returning int(2).
#
# 3. Third, call `array([1, 2])`. The array transformer method doesn't get
#    lark Tokens, it gets a list of transformed values. If we want to extract
#    line and column information, we have to look in the outer scope for the
#    COMMA or RBRACKET tokens, and that's where `inspect` comes in.
#
# Now, it'd probably be nice to also show what file the warning comes from, but
# that information isn't available to the lark parser - it just eats streams.
# We have to ask the JsomParser wrapper around Lark for info about the file -
# so we use method factory methods for dependency injection.


def get_array_transformer(
        parser: JsomParser,
        warnings: bool = True
) -> Callable[[List[JsomValue]], List[JsomValue]]:
    def array_warn(items: List[JsomValue]) -> List[JsomValue]:
        tokens: List[Union[Token], JsomValue] = (
            inspect.stack()[1].frame.f_locals['children']
        )
        # If there is a comma before the closing bracket; this never goes
        # out of bounds since there are two tokens at minimum - an
        # opening and closing brace.
        if isinstance(tokens[-2], Token) and tokens[-2].type == 'COMMA':
            warn(TrailingCommaInArray(line=tokens[-2].line,
                                      column=tokens[-2].column,
                                      near=tokens[-2],
                                      file=parser.file))
        return list(items)

    return array_warn if warnings else list


def get_object_transformer(
        parser: JsomParser,
        warnings: bool = True
) -> Callable[[List[Tuple[str, JsomValue]]], Dict[str, JsomValue]]:
    def object_warn(items: List[Tuple[str, JsomValue]]) -> Dict[str, JsomValue]:
        tokens: List[Union[Token], JsomValue] = (
            inspect.stack()[1].frame.f_locals['children']
        )
        # If there is a comma before the closing brace; this never goes out
        # of bounds since there are two tokens at minimum - an opening and
        # closing brace.
        if isinstance(tokens[-2], Token) and tokens[-2].type == 'COMMA':
            warn(TrailingCommaInObject(line=tokens[-2].line,
                                       column=tokens[-2].column,
                                       near=tokens[-2],
                                       file=parser.file))
        return dict(items)

    def foo(items):
        return dict(items)

    return object_warn if warnings else foo


def get_sqstring_transformer(
        parser: JsomParser,
        warnings: bool = True
) -> Callable[[Token], str]:
    @v_args(inline=True)
    def dqstring_no_warn(token: Token) -> str:
        return literal_eval(token.replace(r'\/', '/'))

    @v_args(inline=True)
    def sqstring_warn(token: Token) -> str:
        warn(
            SingleQuotedString(
                line=token.line,
                column=token.column,
                near=token,
                file=parser.file
            )
        )
        return literal_eval(token.replace(r'\/', '/'))

    return sqstring_warn if warnings else v_args(inline=True)(literal_eval)


def get_identifier_transformer(
        parser: JsomParser,
        warnings: bool = True
) -> Callable[[List[Token]], str]:
    @v_args(inline=True)
    def identifier_no_warn(token: Token) -> str:
        return token.value

    @v_args(inline=True)
    def identifier_warn(token: Token) -> str:
        warn(
            UnquotedString(
                line=token.line,
                column=token.column,
                near=token,
                file=parser.file
            )
        )
        return token.value

    return identifier_warn if warnings else identifier_no_warn


def get_object_item_empty_transformer(
        parser: JsomParser,
        warnings: bool = True
) -> Callable[[Tuple[str]], Tuple[str, JsomValue]]:
    @v_args(inline=True)
    def object_item_empty_no_warn(k: str) -> Tuple[str, None]:
        return k, None

    @v_args(inline=True)
    def object_item_empty_warn(k: str) -> Tuple[str, None]:
        # We have to find the token in the caller's frame
        colon: Token = inspect.stack()[3].frame.f_locals['children'][1]
        warn(
            EmptyObjectValue(
                line=colon.line,
                column=colon.column,
                near=k,
                file=parser.file
            )
        )
        return k, None

    return object_item_empty_warn if warnings else object_item_empty_no_warn

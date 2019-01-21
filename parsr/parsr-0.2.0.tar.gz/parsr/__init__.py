import string
from bisect import bisect_left
from io import StringIO


class Node:
    def __init__(self):
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        return self

    def set_children(self, children):
        self.children.clear()
        for c in children:
            self.add_child(c)
        return self

    def __repr__(self):
        return self.__class__.__name__


def text_format(tree):
    out = StringIO()
    tab = " " * 2
    seen = set()

    def inner(cur, prefix):
        print(prefix + str(cur), file=out)
        if cur in seen:
            return

        seen.add(cur)

        next_prefix = prefix + tab
        for c in cur.children:
            inner(c, next_prefix)

    inner(tree, "")
    out.seek(0)
    return out.read()


def render(tree):
    print(text_format(tree))


class Ctx:
    def __init__(self, lines):
        self.error_pos = -1
        self.error_msg = None
        self.indents = []
        self.tags = []
        self.lines = [i for i, x in enumerate(lines) if x == "\n"]

    def set(self, pos, msg):
        if pos >= self.error_pos:
            self.error_pos = pos
            self.error_msg = msg

    def line(self, pos):
        return bisect_left(self.lines, pos)

    def col(self, pos):
        p = self.line(pos)
        if p == 0:
            return pos
        return (pos - self.lines[p - 1] - 1)


class Parser(Node):
    def __init__(self):
        super().__init__()
        self.name = None

    def map(self, func):
        return Map(self, func)

    @staticmethod
    def accumulate(first, rest):
        results = [first] if first else []
        if rest:
            results.extend(rest)
        return results

    def sep_by(self, sep):
        return Lift(self.accumulate) * Opt(self) * Many(sep >> self)

    def until(self, pred):
        return Until(self, pred)

    def __or__(self, other):
        return Choice([self, other])

    def __and__(self, other):
        return FollowedBy(self, other)

    def __truediv__(self, other):
        return NotFollowedBy(self, other)

    def __add__(self, other):
        return Seq([self, other])

    def __lshift__(self, other):
        return KeepLeft(self, other)

    def __rshift__(self, other):
        return KeepRight(self, other)

    def __mod__(self, name):
        self.name = name
        return self

    def __call__(self, data):
        data = list(data)
        data.append(None)  # add a terminal so we don't overrun
        ctx = Ctx(data)
        ex = None
        try:
            _, ret = self.process(0, data, ctx)
            return ret
        except Exception:
            lineno = ctx.line(ctx.error_pos) + 1
            colno = ctx.col(ctx.error_pos) + 1
            ex = Exception(f"At line {lineno} column {colno}: {ctx.error_msg}")
        if ex:
            raise ex

    def __repr__(self):
        return self.name or f"{self.__class__.__name__}"


class Wrapper(Parser):
    def __init__(self, parser):
        super().__init__()
        self.add_child(parser)

    def process(self, pos, data, ctx):
        return self.children[0].process(pos, data, ctx)


class Seq(Parser):
    def __init__(self, children):
        super().__init__()
        self.set_children(children)

    def __add__(self, other):
        return self.add_child(other)

    def process(self, pos, data, ctx):
        results = []
        for p in self.children:
            pos, res = p.process(pos, data, ctx)
            results.append(res)
        return pos, results


class Choice(Parser):
    def __init__(self, children):
        super().__init__()
        self.set_children(children)

    def __or__(self, other):
        return self.add_child(other)

    def process(self, pos, data, ctx):
        ex = None
        for c in self.children:
            try:
                return c.process(pos, data, ctx)
            except Exception as e:
                ex = e
        raise ex


class Many(Wrapper):
    def process(self, pos, data, ctx):
        results = []
        p = self.children[0]
        while True:
            try:
                pos, res = p.process(pos, data, ctx)
                results.append(res)
            except Exception:
                break
        return pos, results


class Until(Parser):
    def __init__(self, parser, predicate):
        super().__init__()
        self.set_children([parser, predicate])

    def process(self, pos, data, ctx):
        parser, pred = self.children
        results = []
        while True:
            try:
                pred.process(pos, data, ctx)
            except Exception:
                try:
                    pos, res = parser.process(pos, data, ctx)
                    results.append(res)
                except Exception:
                    break
            else:
                break
        return pos, results


class FollowedBy(Parser):
    def __init__(self, p, f):
        super().__init__()
        self.set_children([p, f])

    def process(self, pos, data, ctx):
        left, right = self.children
        new, res = left.process(pos, data, ctx)
        try:
            right.process(new, data, ctx)
        except Exception:
            raise
        else:
            return new, res


class NotFollowedBy(Parser):
    def __init__(self, p, f):
        super().__init__()
        self.set_children([p, f])

    def process(self, pos, data, ctx):
        left, right = self.children
        new, res = left.process(pos, data, ctx)
        try:
            right.process(new, data, ctx)
        except Exception:
            return new, res
        else:
            raise Exception(f"{right} can't follow {left}")


class KeepLeft(Parser):
    def __init__(self, left, right):
        super().__init__()
        self.set_children([left, right])

    def process(self, pos, data, ctx):
        left, right = self.children
        pos, res = left.process(pos, data, ctx)
        pos, _ = right.process(pos, data, ctx)
        return pos, res


class KeepRight(Parser):
    def __init__(self, left, right):
        super().__init__()
        self.set_children([left, right])

    def process(self, pos, data, ctx):
        left, right = self.children
        pos, _ = left.process(pos, data, ctx)
        pos, res = right.process(pos, data, ctx)
        return pos, res


class Opt(Parser):
    def __init__(self, p, default=None):
        super().__init__()
        self.add_child(p)
        self.default = default

    def process(self, pos, data, ctx):
        try:
            return self.children[0].process(pos, data, ctx)
        except Exception:
            return pos, self.default


class Map(Parser):
    def __init__(self, p, func):
        super().__init__()
        self.add_child(p)
        self.func = func

    def process(self, pos, data, ctx):
        pos, res = self.children[0].process(pos, data, ctx)
        return pos, self.func(res)

    def __repr__(self):
        return f"Map({self.func})"


class Lift(Parser):
    def __init__(self, func):
        super().__init__()
        self.func = func

    def __mul__(self, other):
        return self.add_child(other)

    def process(self, pos, data, ctx):
        ex = None
        results = []
        for c in self.children:
            pos, res = c.process(pos, data, ctx)
            results.append(res)
        try:
            return pos, self.func(*results)
        except Exception as e:
            ex = e
        if ex:
            ctx.set(pos, str(ex))
            raise ex


class Forward(Parser):
    def __init__(self):
        super().__init__()
        self.delegate = None

    def __le__(self, delegate):
        self.set_children([delegate])

    def process(self, pos, data, ctx):
        return self.children[0].process(pos, data, ctx)


class EOF(Parser):
    def process(self, pos, data, ctx):
        if data[pos] is None:
            return pos, None
        msg = "Expected end of input."
        ctx.set(pos, msg)
        raise Exception(msg)


class Char(Parser):
    def __init__(self, char):
        super().__init__()
        self.char = char

    def process(self, pos, data, ctx):
        if data[pos] == self.char:
            return (pos + 1, self.char)
        msg = f"Expected {self.char}."
        ctx.set(pos, msg)
        raise Exception(msg)

    def __repr__(self):
        return f"Char('{self.char}')"


class InSet(Parser):
    def __init__(self, s, name=None):
        super().__init__()
        self.values = set(s)
        self.name = name

    def process(self, pos, data, ctx):
        c = data[pos]
        if c in self.values:
            return (pos + 1, c)
        msg = f"Expected {self}."
        ctx.set(pos, msg)
        raise Exception(msg)


class Literal(Parser):
    _NULL = object()

    def __init__(self, chars, value=_NULL, ignore_case=False):
        super().__init__()
        self.chars = chars if not ignore_case else chars.lower()
        self.value = value
        self.ignore_case = ignore_case

    def process(self, pos, data, ctx):
        old = pos
        if not self.ignore_case:
            for c in self.chars:
                if data[pos] == c:
                    pos += 1
                else:
                    msg = f"Expected {self.chars}."
                    ctx.set(old, msg)
                    raise Exception(msg)
            return pos, (self.chars if self.value is self._NULL else self.value)
        else:
            result = []
            for c in self.chars:
                if data[pos].lower() == c:
                    result.append(data[pos])
                    pos += 1
                else:
                    msg = f"Expected case insensitive {self.chars}."
                    ctx.set(old, msg)
                    raise Exception(msg)
            return pos, ("".join(result) if self.value is self._NULL else self.value)


class String(Parser):
    def __init__(self, chars, echars=None):
        super().__init__()
        self.chars = set(chars)
        self.echars = set(echars) if echars else set()

    def process(self, pos, data, ctx):
        results = []
        p = data[pos]
        old = pos
        while p in self.chars or p == "\\":
            if p == "\\" and data[pos + 1] in self.echars:
                results.append(data[pos + 1])
                pos += 2
            elif p in self.chars:
                results.append(p)
                pos += 1
            else:
                break
            p = data[pos]
        if not results:
            msg = f"Expected one of {self.chars}."
            ctx.set(old, msg)
            raise Exception(msg)
        return pos, "".join(results)


class EnclosedComment(Parser):
    def __init__(self, s, e):
        super().__init__()
        Start = Literal(s)
        End = Literal(e)
        p = Start >> AnyChar.until(End).map(lambda x: "".join(x)) << End
        self.add_child(p)

    def process(self, pos, data, ctx):
        return self.children[0].process(pos, data, ctx)


class OneLineComment(Parser):
    def __init__(self, s):
        super().__init__()
        p = Literal(s) >> Opt(String(set(string.printable) - set("\r\n")), "")
        self.add_child(p)

    def process(self, pos, data, ctx):
        return self.children[0].process(pos, data, ctx)


class WithIndent(Wrapper):
    def process(self, pos, data, ctx):
        new, _ = WS.process(pos, data, ctx)
        try:
            ctx.indents.append(ctx.col(new))
            return self.children[0].process(new, data, ctx)
        finally:
            ctx.indents.pop()


class HangingString(Parser):
    def __init__(self, chars):
        super().__init__()
        self.add_child(String(chars) << (EOL | EOF))

    def process(self, pos, data, ctx):
        old = pos
        results = []
        while True:
            try:
                if ctx.col(pos) > ctx.indents[-1]:
                    pos, res = self.children[0].process(pos, data, ctx)
                    results.append(res)
                else:
                    pos = old
                    break
                old = pos
                pos, _ = WS.process(pos, data, ctx)
            except Exception:
                break
        ret = " ".join(results)
        return pos, ret


class StartTagName(Wrapper):
    def process(self, pos, data, ctx):
        pos, res = self.children[0].process(pos, data, ctx)
        ctx.tags.append(res)
        return pos, res


class EndTagName(Wrapper):
    def process(self, pos, data, ctx):
        pos, res = self.children[0].process(pos, data, ctx)
        expect = ctx.tags.pop()
        if res != expect:
            msg = f"Expected {expect}. Got {res}."
            ctx.set(pos, msg)
            raise Exception(msg)
        return pos, res


def make_number(sign, int_part, frac_part):
    tmp = sign + int_part + ("".join(frac_part) if frac_part else "")
    return float(tmp) if "." in tmp else int(tmp)


def skip_none(x):
    return [i for i in x if i is not None]


EOF = EOF()
EOL = InSet("\n\r") % "EOL"
LineEnd = Wrapper(EOL | EOF)
EQ = Char("=")
LT = Char("<")
GT = Char(">")
FS = Char("/")
LeftCurly = Char("{")
RightCurly = Char("}")
LeftBracket = Char("[")
RightBracket = Char("]")
LeftParen = Char("(")
RightParen = Char(")")
Colon = Char(":")
SemiColon = Char(";")
Comma = Char(",")
AnyChar = InSet(string.printable) % "Any Char"
NonZeroDigit = InSet(set(string.digits) - set("0"))
Digit = InSet(string.digits) % "Digit"
Digits = String(string.digits) % "Digits"
Letter = InSet(string.ascii_letters)
Letters = String(string.ascii_letters)
WSChar = InSet(set(string.whitespace) - set("\n\r")) % "Whitespace w/o EOL"
WS = Many(InSet(string.whitespace)) % "Whitespace"
Number = (Lift(make_number) * Opt(Char("-"), "") * Digits * Opt(Char(".") + Digits)) % "Number"
SingleQuotedString = Char("'") >> String(set(string.printable) - set("'"), "'") << Char("'")
DoubleQuotedString = Char('"') >> String(set(string.printable) - set('"'), '"') << Char('"')
QuotedString = Wrapper(DoubleQuotedString | SingleQuotedString) % "Quoted String"

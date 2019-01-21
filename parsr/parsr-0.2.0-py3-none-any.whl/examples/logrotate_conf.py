import string
from parsr import (AnyChar, Choice, EOF, EOL, Forward, LeftCurly, LineEnd, Literal, Many,
                   Number, OneLineComment, Opt, QuotedString, RightCurly,
                   skip_none, String, WS, WSChar)
from parsr.query import Entry


def loads(data):
    return Entry(children=Top(data)[0])


def load(f):
    return loads(f.read())


def to_nodes(x):
    ret = []
    for i in x:
        name, attrs, body = i
        if body:
            for n in [name] + attrs:
                ret.append(Entry(name=n, children=body))
        else:
            ret.append(Entry(name=name, attrs=attrs))
    return ret


scripts = set("postrotate prerotate firstaction lastaction preremove".split())
Stanza = Forward()
Spaces = Many(WSChar)
Bare = String(set(string.printable) - (set(string.whitespace) | set("#{}'\"")))
Num = Number & (WSChar | LineEnd)
Comment = OneLineComment("#").map(lambda x: None)
ScriptStart = WS >> Choice([Literal(s) for s in scripts]) << WS
ScriptEnd = Literal("endscript")
Line = (WS >> AnyChar.until(EOL) << WS).map(lambda x: "".join(x))
Lines = Line.until(ScriptEnd).map(lambda x: "\n".join(x))
Script = ScriptStart + Lines << ScriptEnd
Script = Script.map(lambda x: [x[0], x[1], None])
BeginBlock = WS >> LeftCurly << WS
EndBlock = WS >> RightCurly
First = (Bare | QuotedString) << Spaces
Attr = Spaces >> (Num | Bare | QuotedString) << Spaces
Rest = Many(Attr)
Block = BeginBlock >> Many(Stanza).map(skip_none).map(to_nodes) << EndBlock
Stmt = WS >> (Script | (First + Rest + Opt(Block))) << WS
Stanza <= WS >> (Stmt | Comment) << WS
Doc = Many(Stanza).map(skip_none).map(to_nodes)
Top = Doc + EOF

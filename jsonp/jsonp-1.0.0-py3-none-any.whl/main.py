#!/usr/bin/env python3
import json
import sys

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer


def process(it):
    if len(sys.argv) <= 1:
        dump = json.dumps(it, sort_keys=True, indent=4)
        output = highlight(dump, JsonLexer(), TerminalFormatter())
        print(output, end='')
        return

    print(
        highlight(
            json.dumps(eval(sys.argv[1]), sort_keys=True, indent=4),
            JsonLexer(),
            TerminalFormatter()
        ),
        end=''
    )


def main():
    try:
        stdin = sys.stdin.read()
        it = json.loads(stdin)
        process(it)
    except json.decoder.JSONDecodeError:
        its = [json.loads(line.strip())
               for line in stdin.split('\n') if line.strip()]
        for it in its:
            process(it)


if __name__ == '__main__':
    main()

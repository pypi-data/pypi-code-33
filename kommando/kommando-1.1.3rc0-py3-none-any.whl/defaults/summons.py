"""
MIT License

Copyright (c) 2018 Andre Augusto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
def literal(_ktx, message):
    mention = _ktx.bot.user.mention
    mention2 = mention.replace('<@', '<@!')
    content = message.content
    if mention in message.content:
        message.content = content.replace(mention, '', 1).lstrip()
    elif mention2 in message.content:
        message.content = content.replace(mention2, '', 1).lstrip()
    else:
        return False
    return message

def syntatic(prefix='', suffix=''):
    def _summoning_check(_ktx, message, prefix=prefix, suffix=suffix):
        c = message.content
        if c.startswith(prefix) and c.endswith(suffix):
            if prefix:
                message.content = c[len(prefix):]
            if suffix:
                message.content = c[:-len(suffix)]
            return message
        return False
    return _summoning_check

def chain(*summons):
    def _summoning_check(_ktx, message, summons=summons):
        for x in summons:
            if x(_ktx, message):
                return message
        return False
    return _summoning_check

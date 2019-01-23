'''
help defines an api for printing mold help messages.
'''

import re
import codecs 
import markdown
from mold.util import fs

def read_help_file(ctx, help_file):
    help_file = ctx.MOLD_DOCS + '/' + help_file
    with codecs.open(help_file, mode='r', encoding='utf-8') as help_file:
        help_text = help_file.read()
        return markdown.markdown(help_text)

def replace_non_header_tags(ctx, html):
    reset = ctx.reset
    code_color = ctx.green
    bold_color = ctx.blue
    html = html.replace('</h1>', reset + '</h1>\n')
    html = html.replace('</h2>', reset +'</h2>\n')
    html = html.replace('<blockquote>', '').replace('</blockquote>',  '\n')
    html = html.replace('<blockquote> <p>', '').replace('</p> </blockquote>',  '\n')
    html = html.replace('<p>', '').replace('</p>',  '\n')

    html = re.sub('<br />', '\n', html)
    html = html.replace('<em>', '').replace('</em>', '')
    html = html.replace('<strong>', bold_color + '').replace('</strong>', reset + '')
    html = re.sub('<a.*?>', bold_color, html)
    html = html.replace('</a>', reset)
    html = html.replace('<code>',  code_color + '').replace('</code>', reset + '') # green must appear before '    ' because of strip below
    html = html.replace('<ul>', '').replace('</ul>', '')
    html = html.replace('<li>', '').replace('</li>','' )
    return html.strip()

def force_text_wrap(ctx, text, max_width=80):
    lines = text.split('\n')
    text = ''
    max_width = 80
    for line in lines:
        if len(line) < max_width:
            text += line + '\n'
        else:
            while len(line) > max_width:
                space_index = line.find(' ', max_width)
                text +=  line[:space_index] + '\n'
                line = line[space_index:]
            text += line + '\n'
    return text.strip()

def indent_non_headers(ctx, text):
    lines = text.split('\n')
    text = ''
    for line in lines:
        line = re.sub('\s+', ' ', line).strip()  + '\n' # strip whitespace
        if len(line.strip()) == 0:
            continue
        if line.startswith('<') and not line.startswith('<span'):
            text += line 
        else: 
            text += '    ' + line 
    return text.strip()

def replace_header_tags(ctx, text):
    reset = ctx.reset
    error_color = ctx.red
    header_color = ctx.yellow
    text = text.replace('<h1>', header_color).replace('<h2>', header_color)
    text = text.replace('<h3>', error_color).replace('<h4>', '    ')
    text = re.sub('</h.*>', reset, text)
    text = text.replace('<span/>', '    ')
    text = text.replace('<span />', '    ')
    text = text.replace("<span classname='newline'/>", '')
    text = text.replace("&lt;", '<')
    text = text.replace("&gt;", '>')
    return text.strip()

def print_help(ctx, help_file):
    help_text = read_help_file(ctx, help_file)
    help_text = replace_non_header_tags(ctx, help_text)
    help_text = force_text_wrap(ctx, help_text, 80)
    help_text = indent_non_headers(ctx, help_text)
    help_text = replace_header_tags(ctx, help_text)
    print(help_text)
    return ctx.OK

_no_help_no_command_usage = '''USAGE: mold [--flags] [command] [task] [...options]
    run "mold help" for more info'''

def handle_context(ctx):
    if not ctx.check_help_set():
        if not ctx.command:
            print(_no_help_no_command_usage)
            return ctx.OK
        return ctx.NEXT_COMMAND

    reset = ctx.reset
    error_color = ctx.red
    if ctx.command:
        try:
            help_file = f'{ctx.command}/README.md'
            if ctx.task:
                help_file = f'{ctx.command}/{ctx.command}_{ctx.task}_help.md'
            return print_help(ctx, help_file)
        except:
            if not ctx.task:
                print(f'{error_color}Sorry, mold can not help with:{reset} mold {ctx.command}')
                return ctx.OK
            print(f'{error_color}Sorry, mold can not help with:{reset} mold {ctx.command} {ctx.task}')
            return ctx.OK 
    else:
        print_help(ctx, 'README.md')
        return ctx.OK

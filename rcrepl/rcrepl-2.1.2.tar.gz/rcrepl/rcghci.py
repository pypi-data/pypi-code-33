from .rcrepl import ReplServer, log, start_adapter
import tempfile
import os
import sys
import re

ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def make_error_blocks(content):
    content = ansi_escape.sub('', content)
    errors = []
    warnings = []
    if content is not None and len(content) > 0:
        if "\n\n" in content:
            blocks = content.split("\n\n")
        else:
            blocks = content.split("\r\n")
        for b in blocks:
            lines = b.strip().split("\n")
            for idx, line in enumerate(lines):
                try:
                    (file_name, line, column, type_, msg) = line.split(":")[0:5]
                except Exception as err :
                    continue
                type_ = type_.strip()
                err_msg = "\n".join(lines[idx:])
                full_item =  {'file_name': file_name, 'line': line, 'column' : column, 'text': err_msg }
                if "error" in type_:
                    errors.append(full_item)
                elif "warning" in type_:
                    warnings.append(full_item)
    return {"errors" : errors, "warnings": warnings}

def main():
    COMMAND_PORT = int(os.environ['RCREPL_PORT'])
    try:
        PROMPT = os.environ['RCGHCI_PROMPT']
        if len(PROMPT) < 5:
            raise Exception("ERROR ! Empty or short prompt found. Please use a prompt with more than five characters. You can configure the GHCI prompt by adding the line ':set prompt <prompt>' to ~/.ghci file. Then configure rcghci to use that prompt by setting the RCGHCI_PROMPT env variable using 'export RCGHCI_PROMPT=<prompt>' command from termial, before starting RCGHCI. This is so that RCGHCI script can detect when a command has finished execution.")
    except KeyError:
            raise Exception("ERROR ! The environment variable `RCGHCI_PROMPT` which is supposed to hold the custom ghci prompt was not found. You can set a custom GHCI prompt by adding the line ':set prompt <prompt>' to ~/.ghci file. Then configure rcghci to use that prompt by setting the RCGHCI_PROMPT env variable using 'export RCGHCI_PROMPT=<prompt>' command from termial, before starting RCGHCI. This is so that RCGHCI script can detect when a command has finished execution.")
    start_adapter(sys.argv[1])
    repl_server = ReplServer(PROMPT, "stack", ["ghci"] + sys.argv[2:], ('0.0.0.0', COMMAND_PORT), make_error_blocks)
    repl_server.start()

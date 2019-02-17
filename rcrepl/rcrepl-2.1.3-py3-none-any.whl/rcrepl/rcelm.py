from .rcrepl import WatchServer, log, start_adapter
import tempfile
import os
import sys
import json

class FileMarker:
    def __init__(self):
        self.buffer = {}

    def get_region(self, file_name, line_start, line_end):
        line_start -= 1
        try:
            fcontent = self.buffer[file_name]
        except KeyError:
            with open(file_name, 'r') as fin:
                fcontent = fin.readlines()
                self.buffer[file_name] = fcontent

        return ''.join(["   > {}: {}".format(y+1,x) for (x, y) in zip(fcontent[line_start:line_end], range(line_start, line_end)) ])

def get_msg(x):
    if isinstance(x, str):
        return x
    else:
        return x['string']

def make_error_blocks_elm_18(out):
    items = []
    for out_one in out.split('\n'):
        if len(out_one.strip()) == 0:
            continue;
        try:
            errors = json.loads(out_one)
            fm = FileMarker();
            for error in errors:
                filename = os.path.abspath(error['file'])
                line = error['region']['start']['line']
                line_end = error['region']['end']['line']
                col = error['region']['start']['column']
                tag = error['tag']
                details = error['details']
                error_text = "{}\n    {}\n\n{}".format(tag, details.replace('\n', '\n    '), fm.get_region(filename, line, line_end))
                items.append({'file_name': filename, 'line': line, 'column' : col, 'text': error_text })
        except json.JSONDecodeError as e:
            print("Decoding failed" + str(e))
            print("'{}'".format(out_one))
            pass
    return {"errors" : items, "warnings": []}

def make_error_blocks(content):
    if len(content) == 0:
        return {"errors" : [], "warnings": []}
    else:
        fm = FileMarker();
        try:
            items = []
            errors = json.loads(content)
            for error in errors['errors']:
                for problem in error['problems']:
                    filename = os.path.abspath(error['path'])
                    line = problem['region']['start']['line']
                    line_end = problem['region']['end']['line']
                    col = problem['region']['start']['column']
                    tag = problem['title']
                    details =  ''.join([get_msg(x) for x in problem['message'] ])
                    items.append({'file_name': filename, 'line': line, 'column' : col, 'text': "{}\n{}\n{}".format(tag, details, fm.get_region(filename, line, line_end)) })
            return {"errors" : items, "warnings": []}
        except json.JSONDecodeError as e:
            print("Decoding failed" + str(e))
            pass

def main_(meb):
    COMMAND_PORT = int(os.environ['RCREPL_PORT'])
    start_adapter(sys.argv[1])
    master_server = WatchServer(['elm', 'make', '--report', 'json', *(sys.argv[2:])], ('0.0.0.0', COMMAND_PORT), meb)
    master_server.start()

def main():
    main_(make_error_blocks)

def main18():
    main_(make_error_blocks_elm_18)

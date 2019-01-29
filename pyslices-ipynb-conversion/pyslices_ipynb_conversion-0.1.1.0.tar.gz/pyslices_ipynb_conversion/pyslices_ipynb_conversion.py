import os
import sys
import tempfile

import nbformat as nbf

usrBinEnvPythonText = '#!/usr/bin/env python\n'
pyslicesFormatHeaderText = ['#PySlices Save Format Version 1.1 (PySlices v0.9.7.8 and later)\n',
                            '#PySlices Save Format Version 1.2 (PySlices v0.9.8 and later)\n']
groupingStartText = '#PySlices Marker Information -- Begin Grouping Slice\n'
inputStartText = '#PySlices Marker Information -- Begin Input Slice\n'
outputStartText = '#PySlices Marker Information -- Begin Output Slice\n'

def is_input_marker(s):
    '''Return True for input marker and False for output marker.
       If neither, raise an error.'''
    if s==inputStartText:
        return True
    elif s==outputStartText:
        return False
    else:
        raise ValueError('Grouping markers MUST be followed by input or output markers!')

def first_and_rest(x):
    return x[0], x[1:]

def parse_pyslices_text(text):
    header, groups = first_and_rest(text.split(groupingStartText))
    assert any([i in header for i in pyslicesFormatHeaderText]), 'Not a well-formatted .pyslices file!'
    pyslices_file_version = header.split('Version ')[1].split()[0]
    firsts, rests = zip(*[i.split('\n',1) for i in groups])
    assert all([inputStartText not in i for i in rests]), 'Only one input allowed per group!'
    start_types = [is_input_marker(i+'\n') for i in firsts]
    slices = [i.split(outputStartText) for i in rests]
    inputs_and_outputs = [((s[0] if t else ''), [i[1:] for i in s[t:]])
                          for t, s in zip(start_types, slices)]
    return inputs_and_outputs

class objdict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)

def with_outputs(cell,outputs):
    outputs = outputs if type(outputs)==list else [outputs]
    cell['outputs'] = [objdict(name="stdout", output_type="stream", text=[i])
                       for i in outputs]
    return cell

def make_ipynb_from_pyslices(pyslices_file):
    assert os.path.splitext(pyslices_file)[1]=='.pyslices'
    with open(pyslices_file) as fid:
        r = fid.read()
    i_o = parse_pyslices_text(r)

    text = "This notebook was auto-generated from a .pyslices file"

    cells = [nbf.v4.new_markdown_cell(text)] + \
            [with_outputs(nbf.v4.new_code_cell(i),o)
             for i,o in i_o]

    nb = nbf.v4.new_notebook()
    nb['cells'] = cells
    return nb

def add_nl(x):
    return x if x and x[-1] in '\r\n' else x+'\n'

def make_pyslices_from_ipynb(ipynb_file):
    with open(ipynb_file) as fid:
        nb = nbf.v4.reads(fid.read())

    out_list = [usrBinEnvPythonText, pyslicesFormatHeaderText[-1]]

    for cell in nb.cells:
        if cell.cell_type=='code':
            print(cell)
            out_list += [groupingStartText, inputStartText, add_nl(cell.source)]
            for out in cell.outputs:
                if out.output_type=='stream' and out.name in ['stdout',]: # Need to add error types too...
                    out_list += [outputStartText, '#'+add_nl(out.text)]

    return ''.join(out_list)

def write_ipynb_from_pyslices(pyslices_file, ipynb_file):
    with open(ipynb_file, 'w') as fid:
        nbf.write(make_ipynb_from_pyslices(pyslices_file), fid, 4)

def write_pyslices_from_ipynb(ipynb_file, pyslices_file):
    with open(pyslices_file, 'w') as fid:
        fid.write(make_pyslices_from_ipynb(ipynb_file))

if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="input filename")
    parser.add_argument("-o", "--output", help="output filename")
    parser.add_argument("-f", "--force", help="overwrite the output file if it exists",
                        action="store_true")
    args = parser.parse_args()
    
    
    input_filename = args.input
    input_filename_without_extension, input_ext = os.path.splitext(input_filename)
    
    ext_toggle = {'.pyslices': '.ipynb',
                  '.ipynb': '.pyslices'}
    output_filename = (args.output if args.output is not None else
                       (input_filename_without_extension +
                        ext_toggle[input_ext]))
    
    conversion_fun = (write_ipynb_from_pyslices if input_ext == '.pyslices' else
                      write_pyslices_from_ipynb if input_ext == '.ipynb' else
                      None)
    
    if conversion_fun is None:
        raise Exception('Can only convert between .pyslices and .ipynb files')
    
    if os.path.exists(output_filename) and not args.force:
        print("Overwrite existing file?")
        print(output_filename)
        print("y/n")
        user_input = input()
        if not user_input or user_input[0] != 'y':
            exit()
    
    conversion_fun(input_filename, output_filename)

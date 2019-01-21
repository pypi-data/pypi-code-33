import sys

import os

from kadmos.external.XML_merger.XMLmerger import merge_xmls


def run_tool(analysis_class, sys_argv):
    key_word = analysis_class.__class__.__name__
    key_word_lc = key_word.lower()

    if len(sys_argv) == 1:
        raise SyntaxError('Please provide the required type of run using arguments. Either "--test" or "-i infile.xml '
                          '-o outfile.xml".')
    elif sys_argv[1] == '--test':
        in_file = '__test__{}_input.xml'.format(key_word_lc)
        out_file = '__test__{}_output.xml'.format(key_word_lc)
        with open(in_file, 'w') as f:
            f.write(analysis_class.generate_input_xml())
        analysis_class.execute(in_file, out_file)
        sys.stdout.write('Executed test run of {}.py with input file "{}" and output file "{}".'
                         .format(key_word, in_file, out_file))
    elif sys_argv[1] == '-i':
        in_file = sys_argv[2]
        assert os.path.isfile(in_file), 'Could not find the input file "{}" in the folder.'.format(in_file)
        if '-o' in sys_argv:
            assert sys_argv[3] == '-o', 'Setting "-o" should be the third argument.'
            out_file = sys_argv[4]
        else:
            out_file = '__run__{}_output.xml'.format(key_word_lc)
        analysis_class.execute(in_file, out_file)
        if '-merge-files' in sys_argv:
            assert sys_argv[5] == '-merge-files', 'Setting "-merge-files" should be the fifth argument.'
            assert sys_argv[6] in ['Y', 'y', 'N', 'n'], 'Input argument "-merge-files" can only have value "Y" or ' \
                                                        '"N". Now has value: {}.'.format(sys_argv[6])
            if sys_argv[6] in ['Y', 'y']:
                merge_xmls([in_file, out_file], out_file)
        sys.stdout.write('Executed run of {}.py with input file "{}" and output file "{}".'.format(key_word, in_file,
                                                                                                   out_file))
    else:
        raise SyntaxError('Please provide the required type of run. Either "test" or "-i infile.xml -o outfile.xml".')

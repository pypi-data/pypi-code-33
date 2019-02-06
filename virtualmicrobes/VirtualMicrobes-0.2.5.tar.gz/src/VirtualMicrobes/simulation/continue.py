#! /usr/bin/env python
# encoding: utf-8


import sys
import os

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import itertools

def parse_opts(opt_strings):
    opt_sets = []
    for opt in opt_strings:
        opt_set = []
        try:
            opt, vals = opt.split(':')
            vals = vals.split(';')
            
            for val in vals:
                delims = val.split('-')
                if len(delims) == 2:
                    for v in range(*map(int,delims)):
                        opt_set.append((opt,str(v)))
                else:
                    opt_set.append((opt,val))
            
        except ValueError:
            opt_set.append( (opt,''))
            opt_set.append( ('',''))
        opt_sets.append( opt_set)
    return opt_sets

def to_argparse_opts(opts):
    def parse_opt(opt_string):
        opt,val = opt_string
        if len(opt) == 0:
            return ''
        if len(opt) == 1:
            return '-' + opt + ' ' + val
        return '--' + opt + ' ' + val
    return ' '.join([ parse_opt(opt) for opt in opts ])

def main(argv=None): # IGNORE:C0111
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

    # Setup argument parser
    desc = ('Start a batch of runs. '
            ' Lets you define sets or ranges of parameters for which to run evolutionary simulations.'
            ' All combinations of parameters will be initialized'
            )
    parser = ArgumentParser(description=desc, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('-l', '--load-files' , nargs='+',
                        help='simulation saves to be reloaded and continued'
                        )
    parser.add_argument('-e', '--evo-config' , 
                        help='full path to evolutionary configuration file (should start with evo option'
                        )
    parser.add_argument('-g', '--gen-config' ,
                        help='full path to generation configuration file.'
                        )
    parser.add_argument('-n', '--name', default='continue',
                        help='simulation identification name'
                        )
    parser.add_argument('-a', '--gen-opts', type=str, nargs='*',
                        default=[], 
                        help=('A list of general simulation options [with parameter values (ranges)]. Specify as '
                              ' option-name:val1;val2;val3 OR option-name:start-end OR option-name '
                              ' (without values). e.g. : -a base-death-rate:0.1;0.3;0.5 perfect-mix non:1-3. '
                              ' NOTE: ranges should be integer ranges; they are [start-end) '
                              )
                        )
    parser.add_argument('-z', '--evo-opts', type=str, nargs='*',
                        default=[],
                        help='A list of evolutionary simulation options (see --gen-opts for details)'
                        )
    parser.add_argument('--cores', default=4)
    # Process arguments
    args = parser.parse_args()
    print 'args parsed', args
    gen_opt_sets = parse_opts(args.gen_opts)
    gen_opt_combis = itertools.product(*gen_opt_sets) if len(gen_opt_sets) else [()]
    evo_opt_sets = parse_opts(args.evo_opts)
    evo_opt_combis = itertools.product(*evo_opt_sets) if len(evo_opt_sets) else [()]
    
    sys_commands = ['screen -d -L -t {screen_name} -S {screen_name} -m', 
                    "xvfb-run --auto-servernum --server-args='-screen 0 1024x768x24'",
                    'vermicelli.py', 
                    '-n {cores}']
    
    run_name=args.name
    for lf in args.load_files:
        for gen_opts, evo_opts in itertools.product(gen_opt_combis, evo_opt_combis):
            opt_strings = []
            opt_strings.append('--proctitle vm-{}'.format(run_name))
            name = run_name
            opts_suf = '-'.join([ opt[:3]+val for (opt,val) in gen_opts + evo_opts ])
            if opts_suf != '':
                name += '_'+ opts_suf
            if args.gen_config:
                opt_strings.append( '@' + args.gen_config) 
            opt_strings.append(to_argparse_opts(gen_opts))
            if args.evo_config:
                opt_strings.append( '@' + args.evo_config)
            else:
                opt_strings.append('- evo')
            opt_strings.append(to_argparse_opts(evo_opts))
            opt_strings.append('--name {}'.format(name))
            opt_strings.append("--load-file '{}'".format(lf))
            screen_name = '-'.join([name, lf.split('/')[0]])
            command = ' '.join(sys_commands+opt_strings).format(screen_name=screen_name,cores=args.cores)
            print command
            os.system(command)


    return 0    
    
if __name__ == "__main__":

    sys.exit(main())
#! /usr/bin/env python
# encoding: utf-8


import sys
import os

from argparse import ArgumentParser, RawDescriptionHelpFormatter
import argparse
import itertools
import time

def parse_fixed_opts(opt_strings):
    opt_set = []
    for opt in opt_strings:
        try:
            opt, val = opt.split(':',1) # split on the first occurrence of ':' leaving subsequent ':' in the vals part
            opt_set.append((opt,val))
            
        except ValueError:
            # options will be interpreted as a flag. 
            opt_set.append( (opt,'')) 
    return opt_set

def parse_combining_opts(opt_strings):
    opt_sets = []
    for opt in opt_strings:
        opt_set = []
        try:
            opt, vals = opt.split(':',1) # split on the first occurrence of ':' leaving subsequent ':' in the vals part
            vals = vals.split('+') # use '+' to give different values to be run separately
            # should you want to specify an option that can take multiple arguments and the arguments should be 
            # run simultaneously, you can put the complete argument set between quotes. E.g. the --mutation-rates 
            # option can take multiple arguments for different mutations. To specify different sets of mutation arguments 
            # that should be run together, do something like this:
            # start.py -a mutation_rates:"chrom_dup=0.01 chrom_del=0.01 point_mutation=0.02"+"chrom_dup=0.02 chrom_del=0.02 point_mutation=0.02" ... start
            # this will start runs with either the first full set or the last full set of mutation rate parameters 
                        
            for val in vals:
                delims = val.split('-')
                if len(delims) == 2:
                    for v in range(*map(int,delims)):
                        opt_set.append((opt,str(v)))
                else:
                    opt_set.append((opt,val))
            
        except ValueError:
            # options will be interpreted as a flag. 
            # add options to run with and without the opt-flag.
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
        
    with open('start.log', 'a') as start_log:
        start_log.write('\n{time} : {cl}\n'.format(time=time.strftime("[%H:%M:%S] [%m-%d]"),
                                                   cl=' '.join(sys.argv))
                        )
    # Setup argument parser
    desc = ('Start a batch of runs. '
            ' Lets you define sets or ranges of parameters for which to run evolutionary simulations.'
            ' All combinations of parameters will be initialized'
            )
    parser = ArgumentParser(description=desc, formatter_class=RawDescriptionHelpFormatter)
    parser.add_argument('-s', '--copy-source', type=str, const='~/vermicelli_source', nargs='?',
                        help='copy the vermicelli source path to the current directory. Compile and run local script.')
    parser.add_argument('-c', '--force-recompile', type=str, const='./vermicelli_source', nargs='?',
                        help='force recompilation of a local vermicelli source and run local script.')
    parser.add_argument('-l', '--local-vermicelli', type=str, const='./vermicelli_source/simulation/vermicelli.py', nargs='?', 
                        help='use a (precompiled) local vermicelli.py to run.')
    parser.add_argument('-e', '--run-config' , 
                        help='full path to run type specific configuration file (should start with run-type option)'
                        )
    parser.add_argument('-g', '--gen-config' ,
                        help='full path to general configuration file.'
                        )
    parser.add_argument('-n', '--name', 
                        help='simulation identification name'
                        )
    parser.add_argument('-a', '--gen-opts', type=str, nargs='*',
                        default=[], 
                        help=('A list of general simulation options [with parameter values (ranges)]. Specify as '
                              ' option-name:val1+val2+val3 OR option-name:start-end OR option-name '
                              ' (without values). e.g. : -a base-death-rate:0.1+0.3+0.5 perfect-mix non:1-3. '
                              ' NOTE: ranges should be integer ranges; they are [start-end) '
                              )
                        )
    parser.add_argument('-b', '--fixed-gen-opts', type=str, nargs='*',
                        default=[], 
                        help=('A list of fixed general simulation options [with parameter values (ranges)]. Specify as '
                              ' option-name:val1+val2+val3 OR option-name:start-end OR option-name '
                              ' (without values). e.g. : -a base-death-rate:0.1+0.3+0.5 perfect-mix non:1-3. '
                              ' NOTE: ranges should be integer ranges; they are [start-end) '
                              )
                        )
    parser.add_argument('-y', '--fixed-run-opts', type=str, nargs='*',
                        default=[],
                        help='A list of run-type specific options (see --gen-opts for details)'
                        )
    parser.add_argument('-z', '--run-opts', type=str, nargs='*',
                        default=[],
                        help='A list of run-type specific options (see --gen-opts for details)'
                        )
    parser.add_argument('--cores', type=int)
    parser.add_argument('--dry-run', action='store_true', 
                        default=False, 
                        help='dry run the start script, without actually starting simulations.'
                        )
    parser.add_argument('--no-screen', action='store_false', dest='screen', default=True)
    parser.add_argument('-', dest='__dummy',   # dummy option to parsing of subcommand positional argument
                        action="store_true", help=argparse.SUPPRESS)
    
    subparsers = parser.add_subparsers(help='sub-command specific arguments', dest='run_type')
    
    subparsers.add_parser('start', help='start new sims')
    
    continue_parser = subparsers.add_parser('cont', help='continue a set of saved simulations')
    continue_parser.add_argument('load_files', type=str, nargs='+', 
                                 help='simulation saves to be reloaded and continued')
    continue_parser.add_argument('-f', '--flat', action='store_true',
                                 default=False,
                                 help='continue a simulation in place, in the original directory' 
                                 )
    continue_parser.add_argument('-i', '--in-place', action='store_true', 
                                 help='create the new simulation dir within the dir of the load file.'
                                 )
    
    ancestry_parser = subparsers.add_parser('lod', help='analyze ancestry of a set of saved simulations'
                                            )
    ancestry_parser.add_argument('load_files', type=str, nargs='+', 
                                 help='simulation saves to be reloaded and continued'
                                 )
    ancestry_parser.add_argument('-f', '--flat', action='store_true',
                                 default=False,
                                 help='continue a simulation in place, in the original directory' 
                                 )
    
    # Process arguments
    args = parser.parse_args()
    print
    print 'args parsed', args
    print
    
    ###### copy and/or build source if requested ########
    
    vermicelli = 'vermicelli.py'
    
    if args.copy_source is not None:
        from distutils.dir_util import copy_tree
        source = os.path.expanduser(args.copy_source)
        dir_name = os.path.basename(source)
        dest = os.path.join('.', dir_name)
        copy_tree(source, dest)
        sys.path.append(os.path.abspath(dest))
        import setup
        setup.do_setup(dest, 'start.py', 'build_ext', '--inplace')
        vermicelli = os.path.join(dest,'simulation', vermicelli)
        
    elif args.force_recompile is not None:
        dest = os.path.abspath(args.force_recompile)
        sys.path.append(dest)
        import setup
        setup.do_setup(dest, 'start.py', 'build_ext', '--inplace')
        vermicelli = os.path.join(dest,'simulation', vermicelli)
        
    elif args.local_vermicelli is not None:
        vermicelli = args.local_vermicelli
    
    #####################################################
    fixed_gen_opts = parse_fixed_opts(args.fixed_gen_opts)
    fixed_run_opts = parse_fixed_opts(args.fixed_run_opts)
    
    gen_opt_sets = parse_combining_opts(args.gen_opts)
    gen_opt_combis = itertools.product(*gen_opt_sets) if len(gen_opt_sets) else [()]
    run_opt_sets = parse_combining_opts(args.run_opts)
    run_opt_combis = itertools.product(*run_opt_sets) if len(run_opt_sets) else [()]
    all_opt_combis = list(itertools.product(gen_opt_combis, run_opt_combis))
    if args.run_type=='cont' and args.flat and len(all_opt_combis) > 1:
        parser.error('Can not run multiple option combinations in the same simulation directory.'
                     ' \nopt-combinations:{}'.format(all_opt_combis))
    
    
    sys_commands = []
    if args.screen:
        sys_commands.append( 'screen -d  -L -t {screen_name} -S {screen_name} -m' )
    sys_commands.append("xvfb-run --auto-servernum --server-args='-screen 0 1024x768x24'" )
    sys_commands.append(vermicelli)
    
    
    run_name=args.name if args.name is not None else 'vm'
    if args.run_type=='cont'  and args.load_files is not None:
        run_name += '-cont'
    elif args.run_type=='lod'  and args.load_files is not None:
        run_name += '-lod'
    for comb_gen_opts, comb_run_opts in all_opt_combis:
        gen_opt_strings = []
        run_opt_strings = []
        
        name = run_name
        opts_suf = '-'.join([ opt[:3]+'-'.join(val.strip(' "\'').split()) for (opt,val) in comb_gen_opts + comb_run_opts ])
        if opts_suf != '':
            name += '_' + opts_suf
        if args.gen_config:
            gen_opt_strings.append( '@' + args.gen_config) 
        gen_opt_strings.append('--proctitle {}'.format(run_name))
        gen_opt_strings.append(to_argparse_opts(fixed_gen_opts))
        gen_opt_strings.append(to_argparse_opts(comb_gen_opts))
        if args.cores is not None:
            gen_opt_strings.append('-n {cores}'.format(cores=args.cores))
            
        if args.run_type == 'lod':
            run_opt_strings.append('- ancestry {load_file}')
        elif args.run_type == 'start' or args.run_type == 'cont':
            run_opt_strings.append('- evo')
        if args.run_config:
            run_opt_strings.append( '@' + args.run_config)
            
        run_opt_strings.append(to_argparse_opts(fixed_run_opts))
        run_opt_strings.append(to_argparse_opts(comb_run_opts))
        
        if args.run_type=='start'  or (args.run_type=='cont' and not args.flat):
            run_opt_strings.append('--name {}'.format(name))
        
        # continue a run 
        if args.run_type=='cont'  and args.load_files is not None:
            for lf in args.load_files:
                lf_gen_opt_strings = gen_opt_strings[:]
                if args.in_place:
                    load_path = os.path.dirname(lf)
                    lf_gen_opt_strings.append('--base-dir {}'.format(load_path))
                
                path_components = lf.split('/')
                if len(path_components) > 1:
                    simulation_id = '-'.join([name, path_components[-2]])
                else:
                    simulation_id = name
                    
                commands = sys_commands + lf_gen_opt_strings + run_opt_strings + ["--load-file '{}'".format(lf)]
                if not args.screen:
                    commands.append('> {simulation_id}.log 2>&1 &')
                    command = ' '.join(commands).format(simulation_id=simulation_id)
                else:
                    command = ' '.join(commands).format(screen_name=simulation_id)
                print command, '\n'
                if not args.dry_run:
                    os.system(command)
                    time.sleep(5) # wait a bit for setup
                
        # start lod analysis        
        elif args.run_type=='lod' and args.load_files is not None:
            for lf in args.load_files:
                path_components = lf.split('/')
                if len(path_components) > 1:
                    simulation_id = '-'.join([name, path_components[-2]])
                else:
                    simulation_id = name
                commands = sys_commands + gen_opt_strings + run_opt_strings
                if not args.screen:
                    commands.append('> {simulation_id}.log 2>&1 &') 
                    command = ' '.join(commands).format(load_file=lf, simulation_id=simulation_id)
                else:
                    command = ' '.join(commands).format(load_file=lf, screen_name=simulation_id)
                print command, '\n'
                if not args.dry_run:
                    os.system(command)
                    time.sleep(5) # wait a bit for setup
        else:
            commands = sys_commands + gen_opt_strings +run_opt_strings
            if not args.screen:
                commands.append('> {simulation_id}.log 2>&1 &') 
                command = ' '.join(commands).format(simulation_id=name)
            else:
                command = ' '.join(commands).format(screen_name=name)
            print command, '\n'
            if not args.dry_run:
                os.system(command)
                time.sleep(5) # wait a bit for setup
    return 0    
    
if __name__ == "__main__":

    sys.exit(main())

# Compare all spreadsheets in directory to each other
# Derek Fujimoto
# Nov 2018

import compsheet.multifile_comparer as mc
import os, argparse, sys
from textwrap import dedent

# run if main
if __name__ == '__main__':
    
    # set up argument parser
    parser = argparse.ArgumentParser(description=dedent("""\
        Run a pairwise comparison of all spreadsheets on target PATH. 
        Look for pairs with common features indicative of plagiarism."""),
        formatter_class=argparse.RawTextHelpFormatter)

    # directory
    parser.add_argument("PATH",
                        help='compare spreadsheets found on PATH',
                        action='store',
                        default='.',
                        nargs="?")

    # save all comparisons
    parser.add_argument("-a", "--all",
                        help="write all comparisons to file (default: %d)"%\
                                    mc.cmpr_disp_limit,
                        dest='all',
                        action='store_true',
                        default=False)

    # dry-run don't save spreadsheet
    parser.add_argument("-d", "--dry",
                        help="dry run, don't write to speadsheet",
                        dest='dry',
                        action='store_true',
                        default=False)

    # explain headers
    parser.add_argument("--explain",
                        help='print calculation details and background info',
                        dest='explain',
                        action='store_true',
                        default=False)

    # print lines
    parser.add_argument("-f", "--full",
                        help=dedent("""\
                            print full detailed summary of each comparison 
                                (don't use with a large number of comparisons)"""),
                        dest='full',
                        action='store_true',
                        default=False)

    # log
    parser.add_argument("-l", "--log",
                        help='write printout table to text file',
                        dest='logfile',
                        action='store',
                        default='')
    
    # number of processors
    parser.add_argument("-n", "--nproc",
                        help='choose number of processors for multiprocessing',
                        dest='nproc',
                        action='store',
                        default=1)
    
    # dry-run don't save spreadsheet
    parser.add_argument("-rp", "--relpath",
                        help="use relative path links in output spreadsheet",
                        dest='rel',
                        action='store_true',
                        default=False)    
    # options
    opt_help=dedent("""\
            comma-separated list of items to compare 
                possible: [default] meta, [optional] exact, string, geo, all.
                example: compsheet -o "meta,exact". """)
                    
    parser.add_argument("-o", "--options",
                        help=opt_help,
                        dest='options',
                        action='store',
                        default='meta')
    
    # save as spreadsheet
    parser.add_argument("-s", "--save",
                        help=dedent("""\
                        write printout to xlsx file of this name
                            (default: date)"""),
                        dest='savefile',
                        action='store',
                        default='')
                        
    # print table
    parser.add_argument("-t", "--table",
                        help='print summary table of all comparisons',
                        dest='table',
                        action='store_true',
                        default=False)
    
    # verbose mode
    parser.add_argument("-v", "--verbose",
                        help='print progress output to stdout',
                        dest='verbose',
                        action='store_true',
                        default=False)
    
    # parse
    args = parser.parse_args()

    # -----------------------------------------------------------------------
    # Set up and run comparison
    if args.explain:
        print(mc.explanation)
    
    else:
        try:
            c = mc.multifile_comparer(args.PATH,int(args.nproc),args.rel)
        except IOError as err:
            print(err)
            sys.exit()
        c.compare(options=args.options,do_print=args.full,do_verbose=args.verbose)
        
        # print summary table
        if args.table or args.logfile != '':
            c.print_table(filename=args.logfile)
            
        # save spreadsheet unless dry run
        if not args.dry:
            c.print_spreadsheet(filename=args.savefile,limit_output=not args.all)

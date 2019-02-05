#!/usr/bin/env python3
import os, yaml, sys, glob, json
import argparse
from qualifyr.utility import get_logger
from qualifyr.quality_file import QualityFile
from qualifyr.quast_file import QuastFile
from qualifyr.fastqc_summary_file import FastqcFile
from qualifyr.confindr_file import ConFindrFile
from qualifyr.conditions_file import import_yaml_file
from qualifyr.html_report import create_html_report


class ParserWithErrors(argparse.ArgumentParser):
    logger = get_logger(__file__)
    def error(self, message):
        self.logger.error('{0}\n\n'.format(message))
        self.print_help()
        raise Exception()

    def is_valid_file(self, parser, arg):
        if not os.path.isfile(arg):
            parser.error("The file %s does not exist!" % arg)
        else:
            return arg

def parse_arguments():
    description = """
    A package to check quality files and assess overall pass/fail
    """
    parser = ParserWithErrors(description = description)
    subparsers = parser.add_subparsers(
            help='The following commands are available. Type qualifyr <COMMAND> -h for more help on a specific commands',
            dest='command'
        )
    
    subparsers.required = True

    # check sub command
    check_command = subparsers.add_parser('check', help='Check multiple quality metric files based on conditions and produce overall result')

    check_command.add_argument("-q", "--quast_file",
                        help="quast file path",
                        type=lambda x: parser.is_valid_file(parser, x))
    check_command.add_argument("-f", "--fastqc_file",
                        help="fastqc summary file path",
                        type=lambda x: parser.is_valid_file(parser, x),
                        nargs='+')
    check_command.add_argument("-c", "--confindr_file",
                        help="confindr report file path",
                         type=lambda x: parser.is_valid_file(parser, x))
    check_command.add_argument("-y", "--conditions_yaml_file", required=True,
                        help="conditions yaml file path",
                        type=lambda x: parser.is_valid_file(parser, x))
    check_command.add_argument("-j", "--json_output_format",
                        help="Output the check results as JSON rather than TSV (default)",
                        action='store_true')
    check_command.add_argument("-s", "--sample_name",
                        help="The name of the sample from which the quality files are derived",
                        required = True)
    check_command.add_argument("-o", "--output_dir", help="Path to output directory. If specified output will be written to file in format sample_name.qualifyr.{tsv.json}")

    
    # report sub command
    report_command = subparsers.add_parser('report', help='Produce a html report based on the qualifyr output from multiple sampels')
    report_command.add_argument("-i", "--input_dir", required=True, help="Path to input directory containing multiple qualifyr json outputs")
    report_command.add_argument("-o", "--output_dir", help="Path to output directory")
    report_command.add_argument(
        "-c", "--extra_columns",
        help="Extra columns to add to the report provided as a quote enclosed comma separated list e.g 'quast.N50,quast.# contigs (>= 1000 bp),confindr.contam_status'"
    )
    report_command.add_argument("-t", "--report_title", help="Title for the report", default="Overall Quality Report")

    return parser

def run_check_command(parser, args):
    # load conditions
    conditions = import_yaml_file(args.conditions_yaml_file)
    
    # make list of quality files
    quality_files = []
    # add quast file if present
    if args.quast_file:
        quast_file = QuastFile(args.quast_file)
        quality_files.append(quast_file)
    # add fastqc file if present
    if args.fastqc_file:
        for index, fastqc_file_path in enumerate(args.fastqc_file):
            fastqc_file = FastqcFile(fastqc_file_path, index + 1)
            quality_files.append(fastqc_file)
    # add confindr file if present
    if args.confindr_file:
        confindr_file = ConFindrFile(args.confindr_file)
        quality_files.append(confindr_file)
    
    if len(quality_files) == 0:
        parser.error("You must specify at least one quality file")
    else:
        quality_files = QualityFile.check_multiple_files(quality_files, conditions)
        overall_result = QualityFile.multiple_overall_qc_check_result(quality_files)

        if args.json_output_format:
            output_format= 'json'
            only_failed_checks = False
        else:
            output_format = 'tsv'
            only_failed_checks = True
        
        output_string = QualityFile.multiple_qc_result_string(args.sample_name, quality_files, output_format = output_format, only_failed_checks = only_failed_checks )
        
        if output_format == 'tsv' and not args.output_dir:
            sys.stdout.write('{0}\n'.format(overall_result))

        if args.output_dir:
            with open(os.path.join(args.output_dir, '{0}.qualifyr.{1}'.format(args.sample_name, output_format)), 'w') as outfile:
                outfile.write(output_string)
        else:
            sys.stderr.write(output_string)

def run_report_command(parser, args):
    if not args.output_dir:
        args.output_dir = args.input_dir

    combined_sample_qualifyr_list = []
    extra_columns = []
    for json_file in glob.glob(os.path.join(args.input_dir, '*.qualifyr.json')):
        with open(json_file) as json_fh:
            combined_sample_qualifyr_list.append(json.load(json_fh))

    if args.extra_columns:
        for quality_file, metric_name in [column.split('.') for column in args.extra_columns.split(',')]:
            extra_columns.append({ 'quality_file': quality_file, 'metric_name': metric_name})
            for sample in combined_sample_qualifyr_list:
                if quality_file not in sample['checks'] or metric_name not in sample['checks'][quality_file]:
                    parser.error('Sample {0} does not have data for {1}/{2} as specified in the -c/--extra_columns argument'.format(sample['sample_name'], quality_file, metric_name))

    create_html_report(
        combined_sample_qualifyr_list,
        output_dir =args.output_dir,
        extra_columns = extra_columns,
        title = args.report_title
    )

def choose_command(parser, args):
    if args.command == 'check':
        run_check_command(parser, args)
    elif args.command == 'report':
        run_report_command(parser, args)

def main():
    parser = parse_arguments()
    args = parser.parse_args()
    choose_command(parser, args)




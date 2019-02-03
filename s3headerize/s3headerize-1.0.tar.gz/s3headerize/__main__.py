"""
Set headers on Amazon Web Services (AWS) S3 objects.
"""

import argparse
import logging

import yaml

from s3headerize import BucketHeaderizer


def run_from_cli():
    """ Performs an update instigated by the CLI. """

    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument('--bucket', required=True)
    arg_parser.add_argument('--dry-run', action='store_true')

    arg_parser.add_argument('--header-rules',
                            help='Filename of the header rules',
                            required=True)

    arg_parser.add_argument('--key-prefix')
    arg_parser.add_argument('--log-level', default='INFO')

    args = arg_parser.parse_args()

    logging.basicConfig(level=str(args.log_level).upper())

    with open(args.header_rules, 'r') as stream:
        header_rules = yaml.safe_load(stream.read())

    bucket_headerizer = BucketHeaderizer(dry_run=args.dry_run,
                                         header_rules=header_rules)

    bucket_headerizer.update(bucket=args.bucket, key_prefix=args.key_prefix)


if __name__ == '__main__':
    run_from_cli()

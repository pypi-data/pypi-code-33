import os
import logging

from argparse import ArgumentParser
from metroconv.csv_utils import read_csv_file, write_csv_file
from metroconv.transactions import FromMetroAdapter, Transactions, ToFreeAgentAdapter

parser = ArgumentParser(description='Convert bank CSV transactions between formats (Metro <-> FreeAgent)')
parser.add_argument(metavar='PATH', dest='input_path')
log = logging.getLogger(__name__)


def main():
    logging.basicConfig(level=logging.INFO)
    args = parser.parse_args()

    input_dir, file_name = os.path.split(os.path.abspath(args.input_path))
    source = FromMetroAdapter(read_csv_file(args.input_path))
    transactions = Transactions.from_records(source)

    log.debug(transactions)
    output_file = os.path.join(input_dir, '{}_conv.csv'.format(os.path.splitext(file_name)[0]))

    log.info('Writing output_file: {}'.format(output_file))
    write_csv_file(path=output_file, iterable=ToFreeAgentAdapter(transactions))


if __name__ == '__main__':
    main()

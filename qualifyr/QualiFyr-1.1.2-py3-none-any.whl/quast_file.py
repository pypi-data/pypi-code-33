import csv, sys
from qualifyr.quality_file import QualityFile
from qualifyr.utility import string_to_num, get_logger

class QuastFile(QualityFile):
    logger = get_logger(__file__)
    file_type = 'quast'

    def validate(self):
        # method to check file looks like what it says it is
        '''Returns valid rows from file. An empty list if invalid'''
        with open(self.file_path) as fh:
            reader = csv.reader(fh, delimiter="\t", quotechar='"')
            rows = list(reader)
            first_row = rows[0]
            last_row = rows[-1]
            if first_row[0] == 'Assembly' and last_row[0] == '# N\'s per 100 kbp':
                return rows[1:]
            else:
                return []
    

    def parse(self):
        # read in file and make a dict:
        valid_rows = self.validate()
        if len(valid_rows) == 0:
            self.logger.error('{0} file invalid'.format(self.file_type))
            raise(Exception)

        else:
            for row in valid_rows:
                self.metrics[row[0]] = string_to_num(row[1])




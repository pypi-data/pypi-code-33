#! /usr/bin/env python3

from ftplib import FTP
import os
import re
import argparse

# TO IMPROVE: Make it DRY (not get_genome and get_gtf are copy_pastes)

class Ensembldb(object):
    """ To download ensembl data
    """
    def __init__(self):
        self.url = 'ftp.ensembl.org'

    def __enter__(self):

        self.ftp = FTP(self.url)
        self.ftp.login()
        
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.ftp.quit()
        self.ftp.close()
        
    def get_genome(self, species):
        """Get dna primary sequence from ensembl for the species specified
        """

        path = os.path.join('/', 'pub', 'current_fasta', species, 'dna') 
        self.ftp.cwd(path)
        file_list = self.ftp.nlst()

        pattern = re.compile('.*dna_sm\.primary_assembly\.fa\.gz')
        fas = [fn for fn in file_list if pattern.match(fn)]

        if not fas:
            self.ftp.dir()
            print('No primary assembly are availble for {}'.format(species))
            
        else:
            fas = fas[0]
            print('Downloading {} ...'.format(fas))
            with open(fas, 'wb') as outfile:
                self.ftp.retrbinary('RETR {}'.format(fas), outfile.write)
            
    def get_gtf(self, species):
        """Get the gtf annotation from ensembl for the species specified
        """
        
        path = os.path.join('/', 'pub', 'current_gtf', species) 
        self.ftp.cwd(path)
        file_list = self.ftp.nlst()

        pattern = re.compile('.*\d\.gtf\.gz')
        gtf = [fn for fn in file_list if pattern.match(fn)]

        if not gtf:
            self.ftp.dir()
            print('No gtf available for {}'.format(species))
            
        else:
            gtf = gtf[0]
            print('Downloading {} ...'.format(gtf))
            with open(gtf, 'wb') as outfile:
                self.ftp.retrbinary('RETR {}'.format(gtf), outfile.write)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Library to access databases like Ensembl')
    parser.add_argument('species', nargs='*' )
    return parser.parse_args()
                
if __name__ == '__main__':

    args = parse_arguments()

    with Ensembldb() as ens:
        for species in args.species:
            ens.get_genome(species)
            ens.get_gtf(species)

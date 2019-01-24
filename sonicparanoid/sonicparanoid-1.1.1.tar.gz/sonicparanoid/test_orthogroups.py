#run the main test functions in the group_stats.py module
import orthogroups
from typing import Dict, List
import os



def load_seq_lengths(inDir: str, debug: bool=False) -> Dict[str, Dict[str, int]]:
    """Read input sequences and load sequence lengths."""
    if debug:
        print('\nload_seq_lengths :: START')
        print('Input directory:{:s}'.format(inDir))
    # for each input file it will contain a dictionary with genes and gene lengths
    outDict: Dict[str, Dict[str, int]] = {}
    for el in os.listdir(inDir):
        lenPath: str = os.path.join(inDir, el)
        if el[0] == '.':
            continue
        #print(lenPath)
        if not el in outDict:
            spName = el[:-4]
            outDict[spName] = {}
            # load the entries
            for ln in open(lenPath, 'r'):
                gene, gLen = ln.rstrip('\n').split('\t', 1)
                # add the gene to the dictionary if needed
                if not gene in outDict[spName]:
                    outDict[spName][gene] = int(gLen)
    # return the main dictionary
    return outDict



def main() -> int:
    debug: bool = True
    # get dir with test data
    pySrcDir = os.path.dirname(os.path.abspath(__file__))
    testRoot: str = os.path.join(pySrcDir, 'test/')
    outGrpDir: str = os.path.join(testRoot, 'output_grp_stats/')
    sqlRoot: str = os.path.join(testRoot, 'input_sql/')


    seqLenDir: str = os.path.join(testRoot, 'len_files/')
    #seqLenDir: str = os.path.join(testRoot, 'len_files_20sp/')

    grpFile: str = os.path.join(testRoot, 'input_groups/multispecies_clusters.tsv')
    #grpFile: str = os.path.join(testRoot, 'input_groups/multispecies_clusters_20sp.tsv')
    # MultiParanoid
    #grpFile: str = os.path.join(testRoot, 'input_groups/multiparanoid_out_20_sp_pretty.tsv')

    if debug:
        print('Test directory:\t{:s}'.format(testRoot))
        print('Test Group file:\t{:s}'.format(grpFile))
        print('Test SQL dir:\t{:s}'.format(sqlRoot))
        print('Sequence lengths dir:\t{:s}'.format(seqLenDir))
        print('Test output dir:\t{:s}'.format(outGrpDir))

    # load the sequence lengths
    seqCntDict = load_seq_lengths(inDir=seqLenDir, debug=debug)
    # extract stats
    grpFile = orthogroups.compute_groups_stats(inTbl=grpFile, outDir=outGrpDir, outNameSuffix='test', seqCnts=seqCntDict, debug=debug)

    return 0

if __name__ == "__main__":
    main()

import pandas as pd
from time import time
from ..file_reader import read_file_by_lines
from .. import extract_barcode

def count_barcode(path, output, protocol, min_reads=50, topreads=1000):
    """
    Count the number of the barcodes (), write a count file.
    Usage:
    ::
        from baseqdrops import count_barcode
        count_barcodes("10X.1.fq.gz", "bc.counts.txt", "10X", min_reads=50, topreads=1000)
    
    Args:   
        min_reads (int): The barcode with reads lower than this will be discard (50).
        topreads (str): To process the top N millions of reads (1000).
    
    Returns:
        A csv file of barcode_count, by default (bc.counts.txt)
        cellbarcode/counts
    """

    bc_counts = {}
    start = time()

    print("[INFO] Counting Barcodes For At Most Top {}M Reads Of {}.".format(topreads, path))
    print("[INFO] Barcodes With Less Than {} Reads Are Discarded.".format(min_reads))
    
    index = 0

    lines = read_file_by_lines(path, topreads * 1000 * 1000, 4)

    for line in lines:
        index += 1
        bc = extract_barcode(protocol, line[1])
        if index % 1000000 == 0:
            print("[INFO] Processed top {}M lines. Costs {}s For 1M Reads".format(index/1000000, round(time()-start, 2)))
            start = time()
        if bc == "":
            continue
        if bc in bc_counts:
            bc_counts[bc] += 1
        else:
            bc_counts[bc] = 1

    bc_counts_filter = []
    
    for k, v in bc_counts.items():
        if v >= min_reads:
            bc_counts_filter.append([k, v])

    print("[INFO] Barcode File Is: {}".format(output))
    df = pd.DataFrame(bc_counts_filter, columns=["barcode", "counts"])
    df.to_csv(output, sep=",", index=False)
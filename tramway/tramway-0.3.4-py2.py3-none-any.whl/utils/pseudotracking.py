#!/usr/bin/env python

import numpy  as np
import pandas as pd
import argparse


def reconstruct_trajectory_column(xyt):
    dts = xyt['t'].diff()
    dt = dts.median(skipna=True)
    dts.iloc[0] = dt
    n = np.cumsum(~np.isclose(dts, dt, atol=0, rtol=1e-2))
    n = pd.DataFrame(n, columns=['n'])
    return n.join(xyt)


def main():
    parser = argparse.ArgumentParser(prog='pseudotracking',
        description='fix for xyt files with missing trajectory column')
    parser.add_argument('input_file', help='path to broken "xyt" trajectory file')
    parser.add_argument('output_file', help='path to "nxyt" trajectory file')
    args = parser.parse_args()

    xyt = pd.read_table(args.input_file, names=list('xyt'), sep='   ')
    nxyt = reconstruct_trajectory_column(xyt)
    nxyt.to_csv(args.output_file, sep='\t', header=False, index=False)


if __name__ == '__main__':
    main()


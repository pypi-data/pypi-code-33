test_systems = [
                '1FME',
                '2F4K',
                '2JOF',
                '2WAV',
                'A3D',
                'CLN025',
                'GTT',
                'lambda',
                'NuG2',
                'PRB',
                'UVF',
                'NTL9-0-protein_fixed_CC'
]

from glob import glob

import tables
import h5py
import itertools

files = itertools.chain(*[glob('/group/ag_cmb/marscher/feature_sel/*{sys}*{feat}*.h5'.format(sys=s, feat='backbone')) for s in test_systems]
                        )
import tqdm
for f in tqdm.tqdm(files):
    with h5py.File(f) as fh:
        del fh['backbone']

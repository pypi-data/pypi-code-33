from itertools import product

from sklearn.model_selection import ParameterGrid


class GroupGrid(ParameterGrid):
    def __iter__(self):
        """Iterate over the points in the grid.

        Returns
        -------
        params : iterator over dict of string to any
            Yields dictionaries mapping each estimator parameter to one of its
            allowed values.
        """
        from operator import itemgetter
        for p in self.param_grid:
            # Always sort the keys of a dictionary, for reproducibility
            items = sorted(p.items())
            items = [items[2], items[0], items[1]]
            if not items:
                yield {}
            else:
                keys, values = zip(*items)
                for v in product(*values):
                    params = dict(zip(keys, v))
                    yield params


if __name__ == '__main__':
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
        'NTL9',
    ]

    features = ('xyz',
                'backbone',
                'side_sidechain_torsions',
                'dist_ca',
                'shrake_ruply',
                'res_mindist',
                'res_mindist_d1',
                'res_mindist_d2',
                'res_mindist_expd',
                'res_mindist_c_0.4',
                'res_mindist_c_0.5',
                'res_mindist_c_0.6',
                'res_mindist_c_0.8',
                'res_mindist_c_1.0',
                )

    scores = ('VAMPE', 'VAMP1', 'VAMP2')

    grid = GroupGrid({
        'test_system': test_systems,
        'feature': features,
        'score': scores})

    print('grid len:', len(grid))
    for i, e in enumerate(grid):
        print(i, e)

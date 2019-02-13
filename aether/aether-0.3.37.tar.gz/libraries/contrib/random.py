from __future__ import absolute_import
from collections import Counter
import numpy as np
import six
from six.moves import range

class random(object):

    @staticmethod
    def candidate_sampler(stack, n_samples, replace=True, is_log=False, mask=None):
        if mask is None:
            mask = np.zeros(stack.shape[1:3])
        no_mask = np.where(mask == 0)

        counts = Counter(list(stack[0,:,:,0][no_mask]))

        # Probabilities
        options = list(sorted(counts.keys()))
        if is_log:
            probs = [np.log(counts[o]+1.0) for o in options]
            total = np.sum(probs)
            probs = [p / total for p in probs]
        else:
            probs = [float(counts[o]) for o in options]
            total = np.sum(probs)
            probs = [p / total for p in probs]

        to_include = Counter(np.random.choice(options, size=n_samples, replace=replace, p=probs))

        choices = []
        for value, n_choose in six.iteritems(to_include):
            w = np.where((stack[0,:,:,0]==value) & (mask == 0))
            c = np.random.choice(list(range(len(w[0]))), size=n_choose, replace=replace)
            choices.append(np.array([w[0][c], w[1][c]]))
        choices = np.concatenate(choices, axis=1)

        return choices

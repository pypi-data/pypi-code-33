import os
import re

from collections import Sequence, defaultdict

def get_symmetries(rulestring):

    if rulestring[-1].lower() == 'h':
        validsyms = ["1x256", "2x128", "4x64", "8x32", "C1", "C2_4", "C2_1", "C3_1", "C6",
                 "D2_x", "D2_xo", "D4_x4", "D4_x1", "D6_1", "D6_1o", "D12"]
    else:
        validsyms = ["1x256", "2x128", "4x64", "8x32", "C1", "C2_4", "C2_2", "C2_1", "C4_4", "C4_1",
                 "D2_+2", "D2_+1", "D2_x", "D4_+4", "D4_+2", "D4_+1", "D4_x4", "D4_x1", "D8_4", "D8_1"]

    return validsyms

def validate_symmetry(rulestring, symmetry, throw_error=True):

    if (len(symmetry) > 50):
        if throw_error:
            raise ValueError("%s exceeds maximum of 50 characters" % symmetry)
        return False
    elif (len(symmetry) < 2):
        if throw_error:
            raise ValueError("%s is less than minimum of 2 characters" % symmetry)
        return False

    if not (re.compile("^[a-zA-Z0-9_+]+$").match(symmetry)):
        if throw_error:
            raise ValueError("%s contains an invalid character (not in [a-zA-Z0-9_+])" % symmetry)
        return False

    if "stdin" in symmetry:
        return True

    validsyms = get_symmetries(rulestring)

    redsym = symmetry

    if 'D8_1' in validsyms:
        while ((len(redsym) > 0) and (redsym[0] == 'i')):
            redsym = redsym[1:]

    if throw_error and (redsym not in validsyms):
        raise ValueError("%s is not one of the supported symmetries: %s" % (symmetry, validsyms))

    return (redsym in validsyms)

class SampleSoupList(Sequence):

    def __init__(self, lt, rule, symmetry, samples):

        self.lt = lt
        self.rule = rule
        self.symmetry = symmetry
        self.samples = samples

    def __getitem__(self, i):
        return self.lt.hashsoup(self.rule, self.symmetry, self.samples[i])

    def __len__(self):
        return len(self.samples)

    def __repr__(self):
        return 'SampleSoupList(%r, %r, %r, %r)' % (self.lt, self.rule, self.symmetry, self.samples)

def download_samples(lt, apgcode, rule, domain='https://gol.hatsya.co.uk', tempfile='tempfile'):

    if ('_' in rule) and ('_' not in apgcode):
        rule, apgcode = apgcode, rule

    try:
        from urllib import urlretrieve
    except ImportError:
        from urllib.request import urlretrieve

    url = domain + '/textsamples/' + apgcode + '/' + rule
    urlretrieve(url, tempfile)

    samples = defaultdict(list)

    with open(tempfile, 'r') as f:
        for l in f:
            if '/' not in l:
                continue
            symmetry, seed = tuple(l.strip().split('/')[:2])
            if len(symmetry) > 50:
                continue
            samples[symmetry].append(seed)

    samples = {k : SampleSoupList(lt, rule, k, v) for (k, v) in samples.items() if validate_symmetry(rule, k, False)}
    return samples

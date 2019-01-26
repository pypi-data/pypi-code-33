from .lowlevel import *
from .pattern import Pattern
from .samples import download_samples as dsamples
from .samples import validate_symmetry
import os

from ..genera import sanirule

floats = {}


class Lifetree(object):

    def __init__(self, session, memory=1000, n_layers=None):

        if n_layers is None:
            n_layers = session.default_planes

        self.session = session
        lifelib = session.lifelib
        self.lifelib = lifelib
        self.ptr = lifelib('CreateLifetree', memory, n_layers)
        self.n_layers = n_layers

    def load(self, filename, compressed='deduce', tempfile='tempfile'):

        filename = os.path.abspath(filename)

        if not os.path.isfile(filename):
            raise OSError("%s does not exist or is not a regular file" % filename)

        if compressed == 'deduce':
            compressed = (filename[-3:] == '.gz')

        if compressed:
            import gzip
            import shutil
            with gzip.open(filename, 'rb') as f_in:
                with open(tempfile, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            pptr = self.lifelib('CreatePatternFromFile', self.ptr, tempfile)
            try:
                os.remove(tempfile)
            except OSError:
                pass
        else:
            pptr = self.lifelib('CreatePatternFromFile', self.ptr, filename)

        return Pattern(self.session, pptr, self)

    def hashsoup(self, rule, symmetry, seed):

        validate_symmetry(rule, symmetry)

        pptr = self.lifelib('Hashsoup', self.ptr, rule, symmetry, seed)
        return Pattern(self.session, pptr, self)

    def download_samples(self, apgcode, rule, **kwargs):

        return dsamples(self, apgcode, rule, **kwargs)

    def pattern(self, rle="", rule=None, tempfile='tempfile', verify_apgcode=True):

        tempfile = os.path.abspath(tempfile)
        is_apgcode = False

        if ('=' in rle) or ('[' in rle):
            # Headerful RLE/MC; save and reload:
            with open(tempfile, 'w') as f:
                f.write(rle)
            pptr = self.lifelib('CreatePatternFromFile', self.ptr, tempfile)
            try:
                os.remove(tempfile)
            except OSError:
                pass
        else:
            # Headerless RLE:
            if rule is None:
                if len(self.session.rules) == 1:
                    rule = self.session.rules[0]
                else:
                    raise TypeError("For headerless RLE, rule must be specified unless session has a unique rule")

            rule = self.session.verify_rule(rule)
            pptr = self.lifelib('CreatePatternFromRLE', self.ptr, rle, rule)

            is_apgcode = ('_' in rle) and ('!' not in rle)

        if is_apgcode and (rle[0] != 'x'):
            raise ValueError("Only apgcodes beginning with 'x' contain sufficient information to reconstruct the pattern.")

        pat = Pattern(self.session, pptr, self)

        if is_apgcode and verify_apgcode:
            prefix = rle.split('_')[0]
            prefint = int(prefix[2:])
            period = 1 if (prefix[1] == 's') else prefint

            if (pat[period].centre() != pat.centre()) or (pat.period != period):
                raise ValueError("Pattern does not have the period implied by its apgcode.")

            if (prefix[1] == 's') and (pat.population != prefint):
                raise ValueError("Pattern does not have the population implied by its apgcode.")

            if (verify_apgcode == 'canonical') and (rle != pat.apgcode):
                raise ValueError("The canonical form of %s is %s" % (rle, pat.apgcode))

        return pat

    def __del__(self):

        self.lifelib('DeleteLifetree', self.ptr)

class Session(object):

    def newfloat(self, name):

        if name not in floats:
            floats[name] = 0

        floats[name] += 1
        return ('%s%d' % (name, floats[name]))

    def __init__(self, soname, rules=['b3s23'], local_bash=None,
                 local_python='python', default_planes=4):

        self.default_planes = default_planes
        self.rules = list(rules)
        self.lifelib = WrappedLibrary(soname, local_bash=local_bash, local_python=local_python)

    def lifetree(self, *args, **kwargs):

        return Lifetree(self, *args, **kwargs)

    def verify_rule(self, rule):

        rule = sanirule(rule)

        if (len(rule) > 7) and (rule[-6:] == 'istory'):
            newrule = rule[:-7]
        else:
            newrule = rule

        if newrule not in self.rules:
            raise ValueError("Rule %s is not in the configured rules %s for this session" % (rule, self.rules))

        return rule

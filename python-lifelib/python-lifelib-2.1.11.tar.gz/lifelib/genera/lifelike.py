
from ._iwriter import iwriter

family = 0
bitplanes = 1

def mantissa(rulestring):

    if 'b0' in rulestring:
        return {0, 2, 4, 6, 8}
    else:
        return {0, 1, 2, 3, 4, 5, 6, 7, 8}

def create_rule(rulestring):

    if ('b0' in rulestring) and (rulestring[-1] == '8'):
        raise ValueError('B0 and S8 are incompatible; please invert states.')

    logstring = rulestring[rulestring.index('b'):]
    for iset in [['sse2'], ['sse2', 'avx'], ['sse2', 'avx', 'avx2']]:
        with open('ll_%s_%s.asm' % (iset[-1], logstring), 'w') as f:
            ix = iwriter(f, iset)
            ix.genlogic(logstring)

    with open('iterators_%s.h' % rulestring, 'w') as f:
        f.write('#pragma once\n')
        f.write('#include <stdint.h>\n')
        f.write('#include "../lifeconsts.h"\n')
        f.write('#include "../lifeperm.h"\n')
        f.write('#include "../eors.h"\n')
        f.write('namespace %s {\n\n' % rulestring.replace('-', '_'))

        for iset in [['sse2'], ['sse2', 'avx'], ['sse2', 'avx', 'avx2']]:
            iw = iwriter(f, iset)
            iw.write_function(rulestring, 32, 28)
            iw.write_function(rulestring, 28, 24)
            iw.write_function(rulestring, 24, 20)
            iw.write_function(rulestring, 20, 16)
            iw.write_function(rulestring, 16, 12)
            iw.write_function(rulestring, 12, 8)
            iw.write_iterator()

        f.write('\n#include "../leaf_iterators.h"\n')
        f.write('}\n')

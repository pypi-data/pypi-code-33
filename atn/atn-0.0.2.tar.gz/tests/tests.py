

def test_atn():
    import random
    import pandas as pd
    n = 100
    abeta42 = [random.randrange(600e3, 1800e3)/1e3 for e in range(0, n)]
    ptau = [random.randrange(4e3, 80e3)/1e3 for e in range(0, n)]
    ttau = [random.randrange(97e3, 500e3)/1e3 for e in range(0, n)]
    data = pd.DataFrame(data=[abeta42, ptau, ttau],
        index=['abeta42', 'ptau', 'ttau']).transpose()

    from .. import atn
    staging = atn.stage(data)
    print(atn.staging_summary(staging))

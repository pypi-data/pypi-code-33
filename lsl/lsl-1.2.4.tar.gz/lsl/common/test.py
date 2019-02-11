#!/usr/bin/env python

import idf

proj = idf.parseIDF('test.idf', verbose=True)
print proj.render(verbose=True)
print "===="
for p in proj.generateSDFs(5):
    print p.render(verbose=True)
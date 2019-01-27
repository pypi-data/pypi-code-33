from jivi.oe.Statement.Define import *

from jivi.fs import *
exit()

ar = []
for fp in Dir.files('.',ex='py'):
	n = File.name(fp)
	if n in ['k','__init__']: continue
	ar.append("""from jivi.oe.Statement.Define.{n} import {n}""".format(n=n))
	
	
print("\n".join(ar))
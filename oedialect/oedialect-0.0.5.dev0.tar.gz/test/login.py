import os

#secret_key = 'bb152815-5bf1-42a6-81bb-a3eb35d62241' # Server
OED_CREDS = 'user:12732997043ce2dd210b06e555fea0e39d0df4cc@localhost:8000' # local

#OED_CREDS = 'user:3895c03abaaa04009a1b9ed36ddf1bd069ba88ce@toep.iks.cs.ovgu.de' # toep
#OED_CREDS = 'user:3f1ec0807807b988eacd985d11c60f30203925f2@oep.iks.cs.ovgu.de' # oep

DB_CREDS = 'oedb_test:test@localhost:5432'

os.environ['OEDIALECT_PROTOCOL'] = 'http'
#os.environ['OEDIALECT_VERIFY_CERTIFICATE'] = 'FALSE'
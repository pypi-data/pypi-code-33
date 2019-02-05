from setuptools import setup, Extension

lyra2rec0ban_hash_module = Extension('lyra2rec0ban_hash',
                               sources = [
										  'lyra2rec0banmodule.c',
                                          'Lyra2RE.c',
										  'Sponge.c',
										  'Lyra2.c',
										  'sha3/blake.c',
										  'sha3/groestl.c',
										  'sha3/keccak.c',
										  'sha3/cubehash.c',
										  'sha3/bmw.c',
										  'sha3/skein.c'],
                               include_dirs=['.', './sha3'])

lyra2re2_hash_module = Extension('lyra2re2_hash',
                               sources = [
										  'lyra2re2module.c',
                                          'Lyra2RE.c',
										  'Sponge.c',
										  'Lyra2.c',
										  'sha3/blake.c',
										  'sha3/groestl.c',
										  'sha3/keccak.c',
										  'sha3/cubehash.c',
										  'sha3/bmw.c',
										  'sha3/skein.c'],
                               include_dirs=['.', './sha3'])

lyra2re_hash_module = Extension('lyra2re_hash',
                               sources = [
										  'lyra2remodule.c',
                                          'Lyra2RE.c',
										  'Sponge.c',
										  'Lyra2.c',
										  'sha3/blake.c',
										  'sha3/groestl.c',
										  'sha3/keccak.c',
										  'sha3/cubehash.c',
										  'sha3/bmw.c',
										  'sha3/skein.c'],
                               include_dirs=['.', './sha3'])


setup (name = 'lyra2rec0ban_hash',
       version = '1.0.0',
       author_email = 'c0ban8project@gmail.com',
       author = 'c0ban project',
       url = 'https://github.com/c0ban/lyra2re-hash-python',
       description = 'Bindings for Lyra2REc0ban proof of work used by c0ban',
       ext_modules = [lyra2rec0ban_hash_module, lyra2re2_hash_module, lyra2re_hash_module])

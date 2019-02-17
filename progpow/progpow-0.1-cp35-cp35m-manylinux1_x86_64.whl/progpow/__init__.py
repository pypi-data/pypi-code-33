from ._libprogpow import ffi, lib
from collections import OrderedDict

def get_epoch_num(block_num):
  return block_num//lib.ETHASH_EPOCH_LENGTH

def bytes_to_hash256(bts):
  hash256 = ffi.new("hash256*")
  for i in range(32):
    hash256.bytes[i]=bts[i]
  return hash256

class ProgPowHandler:
  def __init__(self, max_contexts_num=1):
    self.max_contexts_num = max_contexts_num
    self.contexts=OrderedDict()

  def _create_context(self, epoch_num):
    ctx = lib.ethash_create_epoch_context(epoch_num)
    self.contexts[epoch_num]=ctx

  def _destroy_oldest_context(self):
    epoch_num, ctx = self.contexts.popitem(0)
    lib.ethash_destroy_epoch_context(ctx)
 
  def _check_context(self, epoch_num):
    if epoch_num in self.contexts:
      return
    self._create_context(epoch_num)
    while len(self.contexts)>self.max_contexts_num:
      self._destroy_oldest_context()

  def hash(self, header_height, header_hash, nonce):
    hh = bytes_to_hash256(header_hash)
    result = ffi.new("result*")
    epoch_num = get_epoch_num(header_height)
    self._check_context(epoch_num)
    lib.progpow_hash(result, self.contexts[epoch_num], header_height, hh,  nonce) 
    return bytes(result.final_hash.bytes)
    
  def light_search(self, header_height, header_hash, target, start_nonce = 0, iterations=0, step = 2**10):
    hh = bytes_to_hash256(header_hash)
    boundary = bytes_to_hash256(target)
    search_result = ffi.new("search_result*")
    epoch_num = get_epoch_num(header_height)
    self._check_context(epoch_num)
    nonce = start_nonce
    max_nonce = start_nonce+iterations
    while nonce<max_nonce:
      next_iter = step if nonce+step<max_nonce else max_nonce-nonce
      lib.progpow_search_light(search_result, self.contexts[epoch_num], header_height, hh, boundary, start_nonce, next_iter)
      nonce+=next_iter
      if search_result.solution_found:
        break
    if search_result.solution_found:
      return {'solution_found':True, 'nonce':search_result.nonce, 'final_hash':bytes(search_result.final_hash.bytes)}
    else:
      return {'solution_found':False}

  def __del__(self):
    while len(self.contexts):
      self._destroy_oldest_context()

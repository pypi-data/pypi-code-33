#!/usr/bin/python3
# coding=utf-8

import numpy as np

def rms( samples ):
	return np.sum( np.sqrt( np.power( samples, 2 ) ) ) / len( samples )


def rms_envelope( samples, size=20 ):
	return [ rms( samples[ int(np.clip(index-(size/2), 0, len(samples)-1)):int(np.clip(index+(size/2), 0, len(samples)-1)) ] ) for index in range( len( samples ) ) ]


def get_num_chan( samples ):
	if ( type( samples[0] ) == np.ndarray ):
		return len( samples[0] )
	else:
		return 1

def convert_to_float( samples ):
	if( samples.dtype == 'int16' ):
		samples = samples / 32767
	elif( samples.dtype == 'int32' ):
		samples = samples / 2147483647
	elif( samples.dtype == 'int64' ):
		samples = samples / 9223372036854775807
	else:
		print( "Sample Format not implemented... doing nothing!" )
	return samples
#!/usr/bin/python3
# coding=utf-8


import wave
import pyaudio
import numpy as np
from threading import Thread
import scipy.io.wavfile as wavfile
from matplotlib import pyplot as plt









# Complex to Polar Array conversion
def c2p( complexArray ):
    magnitudes = np.sqrt( np.power( complexArray.real, 2 ) + np.power( complexArray.imag, 2 ) )
    phases = np.arctan2( complexArray.imag, complexArray.real )
    return magnitudes, phases

# Polar to Complex Array conversion
def p2c( magnitudes, phases ):
    real = magnitudes * np.cos( phases )
    imag = magnitudes * np.sin( phases )
    return real, imag

# Perform fft on signal. Output is in polar form!!
def fft( data, stringToInt16=False, window=1024, kind='hamming' ):
    if( stringToInt16 ):
        data = np.fromstring( data, dtype=np.int16 )
    if( kind == 'hamming' ):
        fft = np.fft.fft( data * np.hamming( window ) )
    elif( kind == 'hanning' ):
        fft = np.fft.fft( data * np.hanning( window ) )
    elif( kind == 'blackman' ):
        fft = np.fft.fft( data * np.blackman( window ) )
    elif( kind == None ):
        fft = np.fft.fft( data )
    else:
        fft = np.fft.fft( data )
    return c2p( fft )

# Perform ifft on signal (returns only real data). Input is in polar form!!
def ifft( magnitudes, phases, int16ToString=False ):
    real, imag = p2c( magnitudes, phases )
    result = np.zeros( len( magnitudes ), dtype=complex )
    result.real = real
    result.imag = imag
    result = np.array( np.fft.ifft( result ).real, dtype=np.int16 )
    if( int16ToString ):
        result = result.tostring()
    return result


# SIMPLE FFT-IFFT PLAYER FOR SOUND FILE
def play_file_FFT(fname):
    # create an audio object
    wf = wave.open(fname, 'rb')
    p = pyaudio.PyAudio()
    chunk = 1024

    # open stream based on the wave object which has been input.
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # read data (based on the chunk size)
    last_chunk = np.zeros( chunk, dtype=np.int16 )
    next_chunk = np.zeros( chunk, dtype=np.int16 )


    this = np.fromstring( wf.readframes(chunk), dtype=np.int16 )
    _next = np.fromstring( wf.readframes(chunk), dtype=np.int16 )
    thxt = np.concatenate( ( this[(int)(chunk/2):], _next[0:(int)(chunk/2)] ) )

    # play stream (looping from beginning of file to the end)
    while len(_next) >= chunk:
    	

        # FFT        
        this_m, this_p = fft( this, stringToInt16=True, window=chunk )
        next_m, next_p = fft( _next, stringToInt16=True, window=chunk )
        thxt_m, thxt_p = fft( thxt, stringToInt16=True, window=chunk )

        # IFFT
        this_i = ifft( this_m, this_p, int16ToString=False )
        next_i = ifft( next_m, next_p, int16ToString=False )
        thxt_i = ifft( thxt_m, thxt_p, int16ToString=False )

        # OLA
        thxt_i[0:(int)(chunk/2)] += this_i[(int)(chunk/2):]
        thxt_i[(int)(chunk/2):] += next_i[0:(int)(chunk/2)]
        thxt_i = thxt_i.tostring()

        # Write to output
        stream.write(thxt_i)


        # Get next chunk
        this = _next
        _next = np.fromstring( wf.readframes(chunk), dtype=np.int16 )
        thxt = np.concatenate( ( this[(int)(chunk/2):], _next[0:(int)(chunk/2)] ) )        

    # cleanup stuff.
    stream.close()
    p.terminate()


# SIMPLE FFT-IFFT PLAYER FOR SOUND FILE
def scramble_magnitudes_FFT(fname):
    # create an audio object
    wf = wave.open(fname, 'rb')
    p = pyaudio.PyAudio()
    chunk = 1024

    shuffle_index = np.array(range(chunk))
    print(shuffle_index)
    np.random.shuffle(shuffle_index)
    print(shuffle_index)


    # open stream based on the wave object which has been input.
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # read data (based on the chunk size)
    last_chunk = np.zeros( chunk, dtype=np.int16 )
    next_chunk = np.zeros( chunk, dtype=np.int16 )


    this = np.fromstring( wf.readframes(chunk), dtype=np.int16 )
    _next = np.fromstring( wf.readframes(chunk), dtype=np.int16 )
    thxt = np.concatenate( ( this[(int)(chunk/2):], _next[0:(int)(chunk/2)] ) )

    # play stream (looping from beginning of file to the end)
    while len(_next) >= chunk:
    	

        # FFT        
        this_m, this_p = fft( this, stringToInt16=True, window=chunk )
        next_m, next_p = fft( _next, stringToInt16=True, window=chunk )
        thxt_m, thxt_p = fft( thxt, stringToInt16=True, window=chunk )

        '''
        shuffle_index = np.array(range(chunk))
        np.random.shuffle(shuffle_index)
        '''

        # Scramble magnitudes
        this_m = this_m[shuffle_index]
        thxt_m = thxt_m[shuffle_index]
        next_m = next_m[shuffle_index]

        # Scramble phases
        this_p = this_p[shuffle_index]
        thxt_p = thxt_p[shuffle_index]
        next_p = next_p[shuffle_index]


        # IFFT
        this_i = ifft( this_m, this_p, int16ToString=False )
        next_i = ifft( next_m, next_p, int16ToString=False )
        thxt_i = ifft( thxt_m, thxt_p, int16ToString=False )

        # OLA
        thxt_i[0:(int)(chunk/2)] += this_i[(int)(chunk/2):]
        thxt_i[(int)(chunk/2):] += next_i[0:(int)(chunk/2)]
        thxt_i = thxt_i.tostring()

        # Write to output
        stream.write(thxt_i)


        # Get next chunk
        this = _next
        _next = np.fromstring( wf.readframes(chunk), dtype=np.int16 )
        thxt = np.concatenate( ( this[(int)(chunk/2):], _next[0:(int)(chunk/2)] ) )        

    # cleanup stuff.
    stream.close()
    p.terminate()




# SPECTRAL GATE FOR INPUT SOUND FILE
def gate_FFT( fname, threshold=0.005, filename=None):

    # Must convert threshold to int16 value (max is 32767)
    threshold = (int)( threshold * 32767 )
    if( filename != None ):
        rec = np.zeros( 0 )

    # create an audio object
    wf = wave.open(fname, 'rb')
    p = pyaudio.PyAudio()
    chunk = 1024

    # open stream based on the wave object which has been input.
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # read data (based on the chunk size)
    last_chunk = np.zeros( chunk, dtype=np.int16 )
    next_chunk = np.zeros( chunk, dtype=np.int16 )

    
    this = np.fromstring( wf.readframes(chunk), dtype=np.int16 )
    _next = np.fromstring( wf.readframes(chunk), dtype=np.int16 )
    thxt = np.concatenate( ( this[(int)(chunk/2):], _next[0:(int)(chunk/2)] ) )

    # play stream (looping from beginning of file to the end)
    while len( _next ) >= chunk:
    
        # FFT        
        this_m, this_p = fft( this, stringToInt16=True, window=chunk )
        next_m, next_p = fft( _next, stringToInt16=True, window=chunk )
        thxt_m, thxt_p = fft( thxt, stringToInt16=True, window=chunk )

        
        # Calculate noise shape
        if( ( np.sum( np.abs( thxt_m ) ) / len( thxt_m ) ) < threshold ):
            this_m = np.zeros(len(this_m))
            next_m = np.zeros(len(next_m))
            thxt_m = np.zeros(len(thxt_m))


        
        # IFFT
        this_i = ifft( this_m, this_p, int16ToString=False )
        next_i = ifft( next_m, next_p, int16ToString=False )
        thxt_i = ifft( thxt_m, thxt_p, int16ToString=False )

        # OLA & RECORDING
        thxt_i[0:(int)(chunk/2)] += this_i[(int)(chunk/2):]
        thxt_i[(int)(chunk/2):] += next_i[0:(int)(chunk/2)]
        if( filename != None ):
            rec = np.concatenate( ( rec, thxt_i ), axis=0 )
        thxt_i = thxt_i.tostring()


        # Write to output
        stream.write(thxt_i)

        # Get next chunk
        this = _next
        _next = np.fromstring( wf.readframes(chunk), dtype=np.int16 )
        thxt = np.concatenate( ( this[(int)(chunk/2):], _next[0:(int)(chunk/2)] ) )        

    # cleanup stuff.
    stream.close()
    p.terminate()
    if( filename != None ):
        #plt.plot( rec )
        #plt.show()
        wavfile.write( filename, 44100, np.array( rec, dtype=np.int16 ) )




# SPECTRAL DENOISE FOR INPUT SOUND FILE
def denoise_FFT( fname, threshold=0.005, filename=None):

    # Must convert threshold to int16 value (max is 32767)
    threshold = (int)( threshold * 32767 )
    if( filename != None ):
        rec = np.zeros( 0 )

    # create an audio object
    wf = wave.open(fname, 'rb')
    p = pyaudio.PyAudio()
    chunk = 1024

    # open stream based on the wave object which has been input.
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # read data (based on the chunk size)
    last_chunk = np.zeros( chunk, dtype=np.int16 )
    next_chunk = np.zeros( chunk, dtype=np.int16 )

    noise_shape = np.zeros( chunk )

    this = np.fromstring( wf.readframes(chunk), dtype=np.int16 )
    _next = np.fromstring( wf.readframes(chunk), dtype=np.int16 )
    thxt = np.concatenate( ( this[(int)(chunk/2):], _next[0:(int)(chunk/2)] ) )

    # play stream (looping from beginning of file to the end)
    while len( _next ) >= chunk:
    
        # FFT        
        this_m, this_p = fft( this, stringToInt16=True, window=chunk )
        next_m, next_p = fft( _next, stringToInt16=True, window=chunk )
        thxt_m, thxt_p = fft( thxt, stringToInt16=True, window=chunk )

        
        # Calculate noise shape
        if( ( np.sum( np.abs( thxt_m ) ) / len( thxt_m ) ) < threshold ):
            noise_shape += thxt_m
            noise_shape /= 2
            print( noise_shape )


        this_m -= noise_shape
        next_m -= noise_shape
        thxt_m -= noise_shape


        # IFFT
        this_i = ifft( this_m, this_p, int16ToString=False )
        next_i = ifft( next_m, next_p, int16ToString=False )
        thxt_i = ifft( thxt_m, thxt_p, int16ToString=False )

        # OLA & RECORDING
        thxt_i[0:(int)(chunk/2)] += this_i[(int)(chunk/2):]
        thxt_i[(int)(chunk/2):] += next_i[0:(int)(chunk/2)]
        if( filename != None ):
            rec = np.concatenate( ( rec, thxt_i ), axis=0 )
        thxt_i = thxt_i.tostring()


        # Write to output
        stream.write(thxt_i)

        # Get next chunk
        this = _next
        _next = np.fromstring( wf.readframes(chunk), dtype=np.int16 )
        thxt = np.concatenate( ( this[(int)(chunk/2):], _next[0:(int)(chunk/2)] ) )        

    # cleanup stuff.
    stream.close()
    p.terminate()
    if( filename != None ):
        #plt.plot( rec )
        #plt.show()
        wavfile.write( filename, 44100, np.array( rec, dtype=np.int16 ) )

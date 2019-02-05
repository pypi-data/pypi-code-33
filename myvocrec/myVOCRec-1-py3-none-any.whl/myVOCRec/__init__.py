import sys
import glob
import errno
import time
import os
from subprocess import check_output
import queue
import sounddevice as sd
import soundfile as sf
import _thread  

pathy = input("Enter the path to the datasets/audio files directory: ")
name = input("what is your name?    ")
t0 = int(input("Your desired Recording time in seconds:    "))
smr = int(input("sampling rate; 16000 or 42000 or 48000 or 96000 Hz:    "))
bt=int(input("bit depth; 8 or 16 or 24 or 32 bit:    "))

pa00=pathy+"/"+"dataset"+"/"+"audioFiles"+"/"
pa0=pathy+"/"+name+".wav"
pa1=pathy+"/"+"dataset"+"/"+"datanewchi22.csv"
pa2=pathy+"/"+"dataset"+"/"+"stats.csv"
pa3=pathy+"/"+"dataset"+"/"+"datacorrP.csv"
pa4=pathy+"/"+"dataset"+"/"+"datanewchi.csv"
pa5=pathy+"/"+"dataset"+"/"+"datanewchi33.csv"
pa6=pathy+"/"+"dataset"+"/"+"datanewchi33.csv"
pa7=pathy+"/"+"dataset"+"/"+"datanewchi44.csv"
pa8=pathy+"/"+"dataset"+"/"+"essen"+"/"+"MLTRNL.praat"
pa9=pathy+"/"+"dataset"+"/"+"essen"+"/"+"myspsolution.praat"

rere=pa0

RECORD_TIME = t0

def countdown(p,q,w):
    i=p
    j=q
    z=w
    k=0
    while True:
        if(j==-1):
            j=59
            i -=1
        if(j > 9):  
            print(str(k)+str(i)+ " : " +str(j), "\t", end="\r")
        else:
            print(str(k)+str(i)+" : " + str(k)+str(j), "\t", end="\r")
        time.sleep(1)
        j -= 1
        if(i==0 and j==-1):
            break
    if(i==0 and j==-1):
        if z==0:
            huf="Recording start!"
            print(huf)
        if z==1:
            huf="Time up!"
        # time.sleep(1)

print("===========================================")
print("HOLD ON!! get ready, 5 seconds to go!")
print("===========================================")
countdown(0,5,0) #countdown(min,sec)	


q = queue.Queue()
rec_start = int(time.time())

dev_info = sd.query_devices(2, 'input')
# samplerate = int(dev_info['default_samplerate'])
samplerate = smr

def data_callback(input_data, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    q.put(input_data.copy())

with sf.SoundFile(rere, mode='x', samplerate=samplerate, channels=2) as file:
    with sd.InputStream(samplerate=samplerate, device=2, channels=2, callback=data_callback,blocksize=20500):
        rec_time = int(time.time()) - rec_start
        _thread.start_new_thread(countdown,(0,t0,1))
        while rec_time <= RECORD_TIME:
            file.write(q.get())
            rec_time = int(time.time()) - rec_start
print(" ")
print("===========================================")
input("Recording over!! press any key to exit")

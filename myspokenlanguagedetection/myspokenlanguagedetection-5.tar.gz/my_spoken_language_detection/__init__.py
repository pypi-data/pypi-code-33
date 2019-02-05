import glob
import speech_recognition as sr
from langdetect import detect
from langdetect import detect_langs
import numpy as np
import nagisa
import pickle

def myspolangdet(m,p):
    soundi=p+"/"+m+".wav"
    AUDIO_FILE = (soundi)
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        r.energy_threshold = 50
        r.dynamic_energy_threshold = False
        audio = r.record(source, duration=25) # read the entire audio file
    variables = ["en-US", "es-ES", "fr-FR", "it-IT", "de-DE", "pt-PT", "ru-RU","sv-SE","ja-JP"]
    for y in variables:
        try:
            x=r.recognize_google(audio,language = y)
            words = nagisa.tagging(x)
            won=len(words.words)
            print("convergence rate %:   ",won)
            if won>30:
                    x=str(x)
                    c=detect(x)
                    if c=="ja":
                            c="Japanese"
                            print("the language could be:",c) 
            now=len(x.split())
            if now>30:
                    x=str(x)
                    b=detect_langs(x)
                    c=detect(x)
                    
                    if c=="fr":
                            c="French"
                    elif c=="en":
                            c="English"
                    elif c=="es":
                            c="Spanih"
                    elif c=="it":
                            c="Italian"
                    elif c=="de":
                            c="Deutsch"
                    elif c=="ru":
                            c="Russian"
                    elif c=="pt":
                            c="Portuguese"
                    elif c=="sv":
                            c="Swedish"
                    else:
                            c="Out of the list"
                    print("the language could be:",c)
                    
                            			
        except sr.UnknownValueError:
            print("hold on!! ")
        except sr.RequestError as e:
            print("I could not understand audio; {0}".format(e))
    else:
        input("Would you like to try again? ")  



def myspolangESY():
    p = input("Enter the path to the Language_Identification directory: ")
    name = input("what is your name?    ")
    m=str(name)
    soundi=p+"/"+m+".wav"
    AUDIO_FILE = (soundi)
    r = sr.Recognizer()
    with sr.AudioFile(AUDIO_FILE) as source:
        r.energy_threshold = 50
        r.dynamic_energy_threshold = False
        audio = r.record(source, duration=25) # read the entire audio file
    variables = ["en-US", "es-ES", "fr-FR", "it-IT", "de-DE", "pt-PT", "ru-RU","sv-SE","ja-JP"]
    for y in variables:
        try:
            x=r.recognize_google(audio,language = y)
            words = nagisa.tagging(x)
            won=len(words.words)
            print("convergence rate %:   ",won)
            if won>30:
                    x=str(x)
                    c=detect(x)
                    if c=="ja":
                            c="Japanese"
                            print("the language could be:",c) 
            now=len(x.split())
            if now>30:
                    x=str(x)
                    b=detect_langs(x)
                    c=detect(x)
                    
                    if c=="fr":
                            c="French"
                    elif c=="en":
                            c="English"
                    elif c=="es":
                            c="Spanih"
                    elif c=="it":
                            c="Italian"
                    elif c=="de":
                            c="Deutsch"
                    elif c=="ru":
                            c="Russian"
                    elif c=="pt":
                            c="Portuguese"
                    elif c=="sv":
                            c="Swedish"
                    else:
                            c="Out of the list"
                    print("the language could be:",c)
                    
        except sr.UnknownValueError:
            print("hold on!! ")
        except sr.RequestError as e:
            print("I could not understand audio; {0}".format(e))
    else:
        input("Would you like to try again? ")
            

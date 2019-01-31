#!/usr/local/bin/python3
from subprocess import Popen, PIPE
from shlex import split as shsplit
from sys import argv
from json import load
from re import search, split
from nltk import word_tokenize
from os import chdir


class Monitor:
    def __init__(self, project_dir):
        chdir(project_dir)
        self.project_dir = project_dir
        self.events = None

    def get_events(self):
        json_file = open(self.project_dir+'/.settings.json','r') 
        json_data = load(json_file)
        self.events= json_data['events']

    def process_event(self, event_content):
        if len(event_content)<2:
            return
        event_file = event_content[0]
        event_type = event_content[1]
        if event_type in self.events:
            type_action = self.events[event_type]
            for pattern,action in type_action.items():
                if search(pattern, event_file) is not None:
                    print(action)
                    Popen(action, shell=True)
        

    def monitor(self):
        process = Popen(shsplit('fswatch -xr ' + self.project_dir), stdout=PIPE)
        while True:
            event = process.stdout.readline().decode('utf-8')
            print(event)
            event_content = word_tokenize(event)
            if "PlatformSpecific" in event_content:
                event_content.remove("PlatformSpecific")
            if "IsFile" in event_content:
                event_content.remove("IsFile")
            if "IsDir" in event_content:
                event_content.remove("IsDir")
            print(event_content)
            self.process_event(event_content)


def start(project_dir):
    m = Monitor(project_dir)
    m.get_events()
    m.monitor()


    
    
if __name__== "__main__" and len(argv) > 1:
    args = [a for a in argv[1:] if not a.startswith("-")]
    project_dir = args[0]
    start(project_dir)
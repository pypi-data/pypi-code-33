#!/usr/bin/env python
from homevee import Homevee

def main():
    #parse args
    #start homevee server
    homevee = Homevee()
    homevee.start_server()

if __name__ == "__main__":
    main()
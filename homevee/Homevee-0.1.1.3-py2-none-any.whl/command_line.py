#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import sys
from getpass import getpass
from homevee import Homevee

def main():
    homevee = Homevee()

    #parse args
    parser = argparse.ArgumentParser(description='Homevee ist dein neues Smarthome-System!')
    parser.add_argument('--mode', default="start", type=str, help='Modus; default: Homevee starten (start)')
    parser.add_argument('--use_cloud', default=True, type=bool, help='Gibt an, ob die Cloud-Verbindung genutzt werden soll')
    parser.add_argument('--websocket_server', default=False, type=bool, help='Gibt an, ob der Websocket-Server genutzt werden soll')
    parser.add_argument('--http_server', default=False, type=bool, help='Gibt an, ob HTTP-Server genutzt werden soll')
    parser.add_argument('--is_admin', default=False, type=bool, help='Gibt an, ob der neu hinzugefügte Nutzer ein Administrator sein soll')

    args = parser.parse_args()

    print args

    if args.mode == "start":
        start_server(homevee)
    elif args.mode == "add_user":
        add_user(homevee, args.is_admin)

def start_server(homevee):
    homevee.start_server()

def add_user(homevee, is_admin=False):
    username = raw_input("Gib einen Benutzernamen ein: ")
    print username

    password = getpass(prompt="Gib ein Passwort ein:")
    print password

    password_again = getpass(prompt="Wiederhole das Passwort:")
    print password_again

    while(password != password_again):
        print "Die Passwörter stimmen nicht überein!"
        password = getpass(prompt="Gib ein Passwort ein:")
        password_again = getpass(prompt="Wiederhole das Passwort:")

    homevee.add_user(username=username, password=password, is_admin=is_admin)


if __name__ == "__main__":
    main()
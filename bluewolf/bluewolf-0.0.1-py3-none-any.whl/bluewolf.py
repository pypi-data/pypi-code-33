#!/usr/bin/env python

import sys,os
import curses
import pyric
import pyric.pyw as pyw
from pyric.utils.channels import rf2ch
from prettytable import PrettyTable
from proximity import BTSocket
import bluetooth
from multiprocessing.dummy import Pool as ThreadPool
import concurrent.futures
import threading
import time

# GLOBALS

# rssi values store for threaded script
rssi_vals = {}

# FUNCTIONS

# Set the rssi value of an addresss 
def set_rssi(addr, rssi):
    global rssi_vals
    rssi_vals[addr] = rssi

# Get the rssi value of an address asynchronously
def get_rssi(addr, callback, sleep=1):
    b = BTSocket(addr=addr)
    while True:
        rssi = b.get_rssi()
        if rssi is None:
            time.sleep(sleep)
            continue
        callback(addr, rssi)
        time.sleep(sleep)

# Thread wrapper
def start_thread(addr, callback, sleep=1):
    thread = threading.Thread(
            target=get_rssi, 
            args=(),
            kwargs={
                'addr': addr,
                'callback': callback,
                'sleep': sleep
                })
    thread.daemon = True 
    thread.start()
    return thread

# Scan Screen
def scan(stdscr):
    
    # Delay in screen refresh
    curses.halfdelay(5)

    # Set keypress value to 0
    k = 0
    
    # Set up window color scheme
    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_RED)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_YELLOW)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_GREEN)
    curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE) 

    # set flash color
    flash = 1 
    
    # Get list of HW addresses from command line
    addr_list = sys.argv[1:]

    
    # Create a worker thread pool and initialize rssi values to NULL
    threads = []
    for addr in addr_list:
        set_rssi(addr, "NULL")
        th = start_thread(addr=addr, callback=set_rssi)
        threads.append(th)

    # Screen Loop
    while ( k != ord('q')):
        
        # Clean screen
        stdscr.clear()
        stdscr.refresh()

        # Get height and width values of current window
        height, width = stdscr.getmaxyx()
        
        # Loop through HW address list
        index = 1 
        for addr in addr_list:
            
            # get last seen rssi value 
            rssi_val = rssi_vals[addr]
            
            # get absolute value of rssi
            if rssi_val != "NULL":
                rssi_val = abs(int(rssi_val))

            # Create HW address label and add it to the screen
            if rssi_val == 0:
                label = " " + addr + " MAX "
            else:
                label = " " + addr + " " + str(rssi_val) + (4 - len(str(rssi_val))) * " "
            stdscr.addstr(index, 0, label)
            
            # Create proximity bar
            if rssi_val == "NULL":
                bar = ""
            else:
                bar =  " " * (width - abs(int(rssi_val)) - len(label) - 2)
            
            # Add bar to screen and set color
            if rssi_val == "NULL":
                bar = ""
                stdscr.addstr(index, len(label) + 1, bar)
            elif rssi_val == 0:
                stdscr.addstr(index, len(label) + 1, bar, curses.color_pair(flash))
            elif rssi_val <= 10:
                stdscr.addstr(index, len(label) + 1, bar, curses.color_pair(3))
            elif rssi_val <= 50:
                stdscr.addstr(index, len(label) + 1, bar, curses.color_pair(2))
            else:
                stdscr.addstr(index, len(label) + 1, bar, curses.color_pair(1))
            
            # increase vertical index 
            index = index + 1
        
        # Render status bar on bottom of page. TODO Remove last key display (used for debugging)
        statusbarstr = "Press 'q' to exit | Tracking {} devices | Key: {}".format(len(addr_list), k)
        stdscr.attron(curses.color_pair(4))
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(4))
        
        # Set flashing color #mostimportantfeature #bringbackblinktag #hashtagsinpythoncomments #xzibit
        flash = 1 if flash == 3 else 3

        # Wait for exit key
        char = stdscr.getch()
        if char != curses.ERR:
            k = char

# Main screen
def draw_menu(stdscr):
    k = 0

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)
    
    # Disable cursor visibiliy
    curses.curs_set(0)
    
    # Loop where k is the last character pressed
    while (k != ord('q')):

        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()

        # Declaration of strings
        title = "Bluewolf - Bluetooth Device Tracker"[:width-1]
        subtitle = ""[:width-1]
        keystr = "Press spacebar to begin scanning"[:width-1]
        statusbarstr = "Press 'q' to exit"

        # Centering calculations
        start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
        start_x_subtitle = int((width // 2) - (len(subtitle) // 2) - len(subtitle) % 2)
        start_x_keystr = int((width // 2) - (len(keystr) // 2) - len(keystr) % 2)
        start_y = int((height // 2) - 2)

        # Render status bar
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))

        # Turning on attributes for title
        stdscr.attron(curses.color_pair(2))
        stdscr.attron(curses.A_BOLD)

        # Rendering title
        stdscr.addstr(start_y, start_x_title, title)

        # Turning off attributes for title
        stdscr.attroff(curses.color_pair(2))
        stdscr.attroff(curses.A_BOLD)

        # Print rest of text
        stdscr.addstr(start_y + 1, start_x_subtitle, subtitle)
        stdscr.addstr(start_y + 3, (width // 2) - 2, '-' * 4)
        stdscr.addstr(start_y + 5, start_x_keystr, keystr)
        
        # Do the thing
        if k == 32:
            scan(stdscr)
            break

        # Refresh the screen
        stdscr.refresh()

        # Wait for next input
        k = stdscr.getch()

def run():
    curses.wrapper(draw_menu)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Invalid number of arguements")
        print("example: bluewolf 00:11:22:33:44:55 [11:22:33:44:55:66]...")
        sys.exit()
    run()


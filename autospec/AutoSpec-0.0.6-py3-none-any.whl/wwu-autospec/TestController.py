import sys
from tkinter import *

package_loc='/home/khoza/Python/WWU-AutoSpec/wwu-autospec/'
sys.path.append(package_loc)

import goniometer_view
from goniometer_view import TestView


class Controller():
    def __init__(self):
        root=Tk()
        test=TestView(root)
        test.run()


def main():
    control=Controller()
    
if __name__=='__main__':
    main()
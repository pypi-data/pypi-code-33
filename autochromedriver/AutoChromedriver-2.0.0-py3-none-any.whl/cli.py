#!/usr/bin/env python
import sys

import autochromedriver

def main():
    try:
        version = sys.argv[1]
        autochromedriver.download_chromedriver(version=version)
    except:
        autochromedriver.download_chromedriver()

if __name__ == "__main__":
    main()

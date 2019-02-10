#!/usr/bin/python3
if __name__ == "__main__":
    '''
    Simple logging server made to be started in a subprocess. It needs two arguments, a path
    and a the number of logfiles to keep as backup. The path is where the logfiles will be stored
    and must end with the desired name of the logfile.
    '''
    import sys

    from os.path import getsize, isfile
    from logging.handlers import RotatingFileHandler

    def run(file_path):
        with open(file_path, "wb", buffering=0) as logfile:
            while True:
                message = sys.stdin.readline()
                if not message: break
                logfile.write(message.encode())

    if len(sys.argv) == 3:
        logfile = sys.argv[1]
        backups = int(sys.argv[2])

        if isfile(logfile) and getsize(logfile) > 0:
            file_handler = RotatingFileHandler(logfile, backupCount=backups)
            file_handler.doRollover()
        run(logfile)

# -*- coding: utf-8 -*-
"""
Module main.py
----------------
The application main file. 
"""
from tripod import app


def main():
    """The Main application loop.
    Infinitely checks for new entries on the audio source metadata repository . 
    When new files are found on the database, a message is sent to the queue.
    """
    # because they depends on the tripod current app
    # those modules are imported here
    try:
        print('The App is running.....')

    except Exception as ex:
        from tripod import current_app
        import traceback
        current_app.logger.error(str(ex))
        print(traceback.format_exc())
        # exists the application with an error code
        exit(1)


# a call to the main function
if __name__ == "__main__":
    main()
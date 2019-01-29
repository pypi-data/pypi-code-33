######################################################################################
#
# 09/03/2014 jbard v1.2 Added hilight to green, yellow, blue, purple, teal, and white
# 01/28/2018 jbard v1.6 Refactored Codebase for pypi upload
#

version = "1.6"
import os

class cd:
    """ Context manager for changing the current working directory """
    """ 
        class cd()

        Example: 
            with cd(directory):
                print (os.getcwd()) 

            print (os.getcwd()) ## Moves you back to the originating directory on exit
    """
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

class hilight:
    """
        class hilight(string).color(higlight=True, bold=True)

        Example:
            print (hilight("Hello World").red(bold=True))

            Or you could make an object:
                text = hilight("Bar")

                print ("Foo "+text.blue())

            To return the original string:
                print (text.string)
        
        Available Colors:
            red
            green
            yellow
            blue
            purple
            teal
            white
    """
    def __init__(self, string):
        self.string = string


    def red(self, bold=False, highlight=False):
        """ hilight(string).red(bold=False, highlight=False) """
        attr = []

        if highlight:
            attr.append('41')
        else:
            attr.append('31')

        if bold:
            attr.append('1')

        return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), self.string)


    def green(self, bold=False, highlight=False):
        """ hilight(string).green(bold=False, highlight=False) """
        attr = []

        if highlight:
            attr.append('42')
        else:
            attr.append('32')

        if bold:
            attr.append('1')

        return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), self.string)


    def yellow(self, bold=False, highlight=False):
        """ hilight(string).yellow(bold=False, highlight=False) """
        attr = []

        if highlight:
            attr.append('43')
        else:
            attr.append('33')

        if bold:
            attr.append('1')

        return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), self.string)


    def blue(self, bold=False, highlight=False):
        """ hilight(string).blue(bold=False, highlight=False) """
        attr = []

        if highlight:
            attr.append('44')
        else:
            attr.append('34')

        if bold:
            attr.append('1')

        return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), self.string)


    def purple(self, bold=False, highlight=False):
        """ hilight(string).purple(bold=False, highlight=False) """
        attr = []

        if highlight:
            attr.append('45')
        else:
            attr.append('35')

        if bold:
            attr.append('1')

        return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), self.string)


    def teal(self, bold=False, highlight=False):
        """ hilight(string).teal(bold=False, highlight=False) """
        attr = []

        if highlight:
            attr.append('46')
        else:
            attr.append('36')

        if bold:
            attr.append('1')

        return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), self.string)


    def white(self, bold=False, highlight=False):
        """ hilight(string).white(bold=False, highlight=False) """
        attr = []

        if highlight:
            attr.append('47')
        else:
            attr.append('37')

        if bold:
            attr.append('1')

        return '\x1b[%sm%s\x1b[0m' % (';'.join(attr), self.string)


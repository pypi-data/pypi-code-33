from py_asa_loader import Loader
from py_asa_loader import util
import progressbar
import argparse
import time
import sys

def argHandler():
    parser = argparse.ArgumentParser(description='Load program to ASA series board.')
    parser.add_argument('-H', '--hex',
                        dest='hexfile', action ='store', type = str,
                        help='assign hex file to be load')
    parser.add_argument('-p', '--port',
                        dest='portnum', action ='store', type = str,
                        help='assign the port to load')
    args = parser.parse_args()
    return args

def run():
    args = argHandler()

    loader = Loader(args.portnum ,args.hexfile)
    print('program size: {:0.2f} KB'.format(loader.dataSize))

    widgets=[
        ' [', progressbar.Timer(), '] ',
        progressbar.Bar(),
        progressbar.Counter(format='%(percentage)0.2f%%'),
    ]
    bar = progressbar.ProgressBar(max_value=loader.total_steps, widgets=widgets)
    bar.update(0)

    for i in range(loader.total_steps):
        try:
            loader.step()
        except util.ChkDeviceException as e:
            bar.finish(end='\n', dirty=True)
            print('Error: The device is not asa-board.')
        except util.CantOpenComportException as e:
            bar.finish(end='\n', dirty=True)
            print('Error: Cannot open the comport \'{}\'.'.format(loader.port))
            print('    Please check the arg port is right and the comport is not in used.')
            print('    The arg \'port\' shoule be like \'COM1\', \'COM2\'...')
            break
        except util.EndingException as e:
            bar.finish(end='\n', dirty=True)
            print('Error: The device ignored the ending command .')
            break

if __name__ == '__main__':
    run()

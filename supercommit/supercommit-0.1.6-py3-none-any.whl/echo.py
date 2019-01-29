from click import echo

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

'''
echo normal style message
'''
def normal(message):
    echo(message)

'''
echo warning leve message
'''
def warning(message):
    echo(WARNING+str(message))

'''
echo error leve message
'''
def error(message):
    echo(FAIL+str(message))

'''
echo success leve message
'''
def success(message):
    echo(OKGREEN+str(message))

'''
echo info leve message
'''
def info(message):
    echo(OKBLUE+str(message))
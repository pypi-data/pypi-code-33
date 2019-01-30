"""
========
Espresso
========


Webs

"""


import gc
import uos
import utime
import ujson
import urandom
import network
from uio import BytesIO
from machine import Timer

from .websockets import client

BOOT = '/boot.py'
DEBUG = False
ON_REPL = False
TIME_REQUEST = 200
PING_TIMEOUT = 30000
TIME_CONNECTION = 500
WEBSOCKET_TIMEOUT = 2

STATUS_WIFI = False
STATUS_SERVER = False

_timer = None
_ping = 0
_activated = ["import espresso", "espresso.start()"]
_deactivated = ["#import espresso", "#espresso.start()"]
_espresso_conf_file = '/espresso.conf'


# ----------------------------------------------------------------------
def load_config(filename=_espresso_conf_file):
    """"""
    try:
        with open(filename, 'r') as file:
            config = ujson.load(file)
    except:
        config = {}
    return config


# ----------------------------------------------------------------------
def save_config(config, filename=_espresso_conf_file):
    """"""
    with open(filename, 'w') as file:
        ujson.dump(config, file)


# ----------------------------------------------------------------------
def gen_key():
    """"""
    urandom.seed(utime.ticks_add(utime.ticks_ms(), utime.ticks_cpu()))
    chain = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890123456789'
    try:
        KEY = ''.join(urandom.choice(chain) for i in range(16))
    except TypeError as e:
        KEY = None

    return KEY


# ----------------------------------------------------------------------
def register_in_server():
    """Send chain for register device on websocket server."""

    global websocket, STATUS_SERVER
    utime.sleep_ms(TIME_CONNECTION)  # limit calls to this funtion to avoid max recursion

    if DEBUG:
        print('Espresso: Connecting with websockets...')

    for address in espresso_conf.get('WEBSOCKETS', []):

        try:
            if DEBUG:
                print('Espresso: Tring {}'.format(address))

            websocket = client.connect(address)
            if DEBUG:
                print('Espresso: Connected to {}'.format(address))
                print('Espresso: Registering...')

            websocket.settimeout(WEBSOCKET_TIMEOUT)

            # send register chain
            data = DATA.copy()
            data['action'] = 'register'
            websocket.send(ujson.dumps(data))
            STATUS_SERVER = True
            return

        except:
            if DEBUG:
                print('Espresso: Fail {}'.format(address))

    register_in_server()


# ----------------------------------------------------------------------
def connect_to_wifi():
    """Try to connect to WiFi network.

    If espresso_conf contain NETS will use them for attempt connection.
    """
    global sta_if, STATUS_WIFI

    # if network list connections available
    if 'NETS' in espresso_conf:

        # will not end until connection established
        while not sta_if.isconnected():
            for net, passw in espresso_conf['NETS']:
                sta_if.active(True)
                sta_if.connect(net, passw)
                utime.sleep_ms(TIME_CONNECTION)  # limits speed call

                if sta_if.isconnected():  # finally!!!
                    STATUS_WIFI = True
                    return True
        return True

    return False


# ----------------------------------------------------------------------
def run_on_exec(script):
    """Compile and Exec sccrip.

    Parameters
    ----------
    script : str
        Python script to be executed.

    """
    compiled = compile(script + '\n', '<string>', 'exec')
    exec(compiled, locals(), locals())


# ----------------------------------------------------------------------
def read_chunk(path, size=1024):
    """Read big files.
    
    MicroPython will return a `memory allocation failed` due RAM capcity,
    so the files must be readed N bytes at time.
    
    Parameters
    ----------
    path: str
        File path for read.
    size: int
        Size of buffer used for read the file.
        
    """
    global websocket

    file_obj = open(path, 'r')
    data = DATA.copy()
    data['action'] = 'stream'
    sub_data = {'response': '',
                'path': path,
                'snippet': 'readfile',
                }
    data['data'] = sub_data
    websocket.send(ujson.dumps(data))
    while True:
        data_chunk = file_obj.read(size)
        if data_chunk:
            data = DATA.copy()
            data['action'] = 'stream'
            sub_data = {'response': data_chunk,
                        'path': path,
                        'snippet': 'readchunk',
                        }
            data['data'] = sub_data
            websocket.send(ujson.dumps(data))
        else:

            data = DATA.copy()
            data['action'] = 'stream'
            sub_data = {'response': '\n',
                        'path': path,
                        'snippet': 'readchunk',
                        }
            data['data'] = sub_data
            websocket.send(ujson.dumps(data))

            break


# ----------------------------------------------------------------------
def espresso_repl(t):
    """Run command received from websockets.

    Main function responsible to get scripts from websockets and interpret them,
    also check connections to WiFi and Wesockets (and restores them if necessary).

    Parameters
    ----------
    t: int
        Timer argumment.

    """
    global sta_if, websocket, ON_REPL, _timer, _ping, STATUS_WIFI, STATUS_SERVER

    if DEBUG:
        print('Espresso: REPL', ON_REPL)

    # No overlap calls to this funtion, for scripts that take a long time
    if ON_REPL:
        return

    ON_REPL = True
    uos.chdir('/')

    # reset WiFi if disconnected
    if not sta_if.isconnected():
        STATUS_WIFI = False
        connect_to_wifi()

    # create Websocket connection if not established
    if websocket is None or not websocket.open:
        STATUS_SERVER = False
        register_in_server()

    # check Websocket connection
    if _ping >= PING_TIMEOUT:
        _ping = 0
        try:
            websocket.send('')
        except:
            register_in_server()
    else:
        _ping += TIME_REQUEST

    # receive script
    try:
        script = websocket.recv()
    except:
        script = None
        pass

    if script:

        # duplicate the stdout and creane new one in BytesIO
        espresso_stdout = BytesIO()
        uos.dupterm(espresso_stdout)

        # run script
        gc.collect()
        try:
            run_on_exec(script)
            out = espresso_stdout.getvalue().decode()
        except Exception as e:  # if script contain errors
            out = espresso_stdout.getvalue().decode()
            out += '\n' + str(e)
        gc.collect()

        # send result to webocket
        data = DATA.copy()
        data['action'] = 'stream'
        data['data'] = out

        try:
            websocket.send(ujson.dumps(data))
        except:
            register_in_server()

    # unlock calls
    ON_REPL = False


# ----------------------------------------------------------------------
def enable():
    """Edit boot.py for add autostart Espresso.
    
    By default add a `start(0)`
    """
    # Read current boot status
    with open(BOOT, 'r') as file:
        content = file.read()

    for s in _deactivated + _activated:
        content = content.replace(s, '')

    with open(BOOT, 'w') as file:
        file.write('{}\n{}\n{}'.format(content.strip('\n'), *_activated))


# ----------------------------------------------------------------------
def disable():
    """Edit boot.py for remove autostart Espresso."""

    # Read current boot status
    with open(BOOT, 'r') as file:
        content = file.read()

    for s in _deactivated + _activated:
        content = content.replace(s, '')

    with open(BOOT, 'w') as file:
        file.write('{}\n{}\n{}'.format(content.strip('\n'), *_deactivated))


# ----------------------------------------------------------------------
def stop():
    """Kill timer."""

    global _timer
    if _timer != None:
        _timer.deinit()
    _timer = None


# ----------------------------------------------------------------------
def _start():
    """Slave start funtion..
    
    Returns
    -------
    bool
        True if connected, False otherwise.
    
    """
    global sta_if, websocket, _timer

    sta_if = network.WLAN(network.STA_IF)
    websocket = None
    # first of all, check a WiFi conection
    if connect_to_wifi():
        _timer = Timer(-1)
        _timer.init(period=TIME_REQUEST, mode=Timer.PERIODIC, callback=espresso_repl)
        return True
    else:
        utime.sleep_ms(TIME_CONNECTION)
        return False


# ----------------------------------------------------------------------
def start(attempts=0):
    """Start espresso Websocket REPL.

    Parameters
    ----------
    attempts: int
        Number of attempts to try a connection before give up.
         * 0: One attempt
         * -1: Infinite attempts
         * >0: N attempts

    """
    # Try to connect a limitated number of times
    if attempts >= 1:
        if DEBUG:
            print('Espresso: {} attempts'.format(attempts))
        for attempt in range(attempts):
            if _start():
                return

    # Try to connect just one time.
    elif attempts == 0:
        if DEBUG:
            print('Espresso: single shot')
        if _start():
            return

    # Try to connect all time, no limit.
    elif attempts == -1:
        if DEBUG:
            print('Espresso: infinite loop')
        while True:
            if _start():
                return


espresso_conf = load_config()

if not 'KEY' in espresso_conf:
    espresso_conf['KEY'] = gen_key()

if not 'WEBSOCKETS' in espresso_conf:
    espresso_conf['WEBSOCKETS'] = [
        'ws://espresso.yeisoncardona.com/ws',
        'ws://yeisoncardona.com:3200/ws',
        'ws://188.166.6.6:3200/ws',
    ]

DATA = {
    'id': espresso_conf['KEY'],
    'type': 'device',
}

try:
    save_config(espresso_conf)
except:
    pass

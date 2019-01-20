"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from __future__ import print_function
import os
import errno
import subprocess
import hashlib
import sys
from time import sleep
import requests
import json
import signal
import threading
from thread import get_ident
import zipfile
import logging

from .common import JemuConnectionException
from .timeout_dec import timeout
from .common import \
    TimeoutException,\
    VlabException,\
    EmulationError,\
    MissingFileError,\
    ArgumentError
from .jemu_bsp_parser import JemuBspParser
from .jemu_gpio import JemuGpio
from .jemu_connection import JemuConnection
from .jemu_web_api import JemuWebApi
from .analytics import Analytics
from .jemu_interrupts import JemuInterrupts
from .jemu_uart_json import JemuUartJson as JemuUart
from .jemu_vars import SSL_ENV, JEMU_PATH, OBJDUMP_PATH, OBJCOPY_PATH
from .config import get_token
from .login import login
from .platforms import platforms_default_config_dict, platforms_list_lower
from .user_error_reporting import UserErrorReporting
from .version_check import check_sdk_version


class Vlab (object):
    """
    The main class for using Jumper Virtual Lab

    :param working_directory: The directory that holds the board.json abd scenario.json files for the virtual session
    :param config_file: Config file holding the API token (downloaded from https://vlab.jumper.io)
    :param gdb_mode: If True, a GDB server will be opened on port 5555
    :param sudo_mode: If True, firmware can write to read-only registers. This is useful for injecting a mock state to the hardware.
    :param registers_trace: Adds a trace for CPU registers values before every CPU instruction.
    :param functions_trace: Adds a trace for the the functions that are being executed (requires a .out or .elf file)
    :param interrupts_trace: Adds a trace for interrupts handling.
    :param trace_output_file: If traces_list is not empty, redirects the trace from stdout to a file.
    :param print_uart: If True UART prints coming from the device will be printed to stdout or a file.
    :param uarts_to_print: List of uarts that will be print to stdout, in case print_uart=True. If the list is empty and print_uart=True, all the uarts print. 
    :param uart_output_file: If print_uart is True, sets the UART output file. Default is stdout.
    :param uart_device: If True, a "uart" file will be created in the working directory which is linked to the virtual UART device. Can be used with "screen". Linux only
    :param token: The API token to be used for authentication. If not specified, the token in ~/.jumper/config.json will be used.
    :param platform: Emulated platform, should only be when no board.json file exists in the working directory. If no platform is specified and board.json is not used, "nrf52832" is assumed.
    :param print_mips: If True, print MIPS (Million instructions per second) when emulation is finished.
    """

    _INT_TYPE = "interrupt_type"
    _DESCRIPTION = "description"
    _TYPE_STRING = "type"
    _BKPT = "bkpt"
    _VALUE_STRING = "value"
    _ERROR = "error"
    _EXAMPLES_HASH_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), 'examples_hash_list.json'))

    def __init__(
            self,
            working_directory=None,
            config_file=None,
            gdb_mode=False,
            sudo_mode=False,
            registers_trace=False,
            functions_trace=False,
            interrupts_trace=False,
            trace_output_file=None,
            print_uart=False,
            uart_output_file=None,
            uart_device=False,
            platform=None,
            token=None,
            debug_peripheral=False,
            gpio=False,
            stack_max=False,
            code_coverage=False,
            print_mips=False,
            uarts_to_print=[]
    ):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self._logger.addHandler(handler)
        args = locals()
        self._local_jemu = True if \
            ('LOCAL_JEMU' in os.environ and os.environ['LOCAL_JEMU'] == '1') or \
            ('JEMU_LOCAL' in os.environ and os.environ['JEMU_LOCAL'] == '1') \
            else False
        check_sdk_version(self._local_jemu)
        self._working_directory = os.path.abspath(working_directory) if working_directory else os.getcwd()
        self._working_directory_dot_jumper = os.path.join(self._working_directory, '.jumper')
        self._gdb_mode = gdb_mode
        self._sudo_mode = sudo_mode
        self._code_coverage = code_coverage
        self._mips = print_mips
        self._jemu_process = None
        self._components = []
        self._platform = platform if platform != 'stm32f4' else 'stm32f411'
        self._debug_peripheral = debug_peripheral
        self._was_start = False
        self._program_file = None
        self._program_elf = os.path.join(self._working_directory_dot_jumper, 'program.elf')
        self._remove_pty_if_exist()
        self._jemu_server_address = "localhost"
        self._jemu_connection = JemuConnection(self._jemu_server_address)
        self._uart_device = uart_device
        self._registers_trace = registers_trace
        self._functions_trace = functions_trace
        self._interrupts_trace = interrupts_trace
        self._trace_output_file = trace_output_file
        self._print_uart = print_uart
        self._uart_output_file = uart_output_file
        self._jemu_debug = True if 'JEMU_DEBUG' in os.environ else False
        self._jemu_port = 8000 if self._jemu_debug else 0
        self._on_bkpt = None
        self._on_exit = None
        self._jemu_connection.register(self.receive_packet)
        self._jemu_interrupt = JemuInterrupts()
        self._user_error_reporting = UserErrorReporting(self._working_directory_dot_jumper)
        self._threads = []
        self._stdout_thread = None
        self._peripherals_json_parser = None
        self._build_components_methods()
        self._uarts_to_print = uarts_to_print
        self._set_uarts_to_print()
        self._jemu_gpio = JemuGpio(self.SUDO)
        self._firmware = None
        self._new_signature = None
        self._web_api = None
        self._analytics = None
        self._traces = self._aggregate_traces()
        self._jemu_port_file = os.path.join(self._working_directory_dot_jumper, "port")
        self._gpio_flag = gpio
        self._stack_max_ = stack_max
        self._error_string = None
        self._exit_lock = threading.Lock()

        # Assing on of the UARTs to the self._uart for backward compatible
        if self._platform.find("stm") != -1:
            self._uart = self.USART2 # stm default uart is USART2


        else:
            # Not stm - choose the first uart in the list
            for component in self._components:
                if component['type'] == 'uart':
                    self._uart = component['obj']
                    break


        self._jemu_connection.register(self._unsupported_instruction_callback)
        try:
            if not os.path.exists(self._working_directory_dot_jumper):
                os.makedirs(self._working_directory_dot_jumper)

            force_config_ = True if ('FORCE_CONFIG_TEST' in os.environ) else False
            if (not self._local_jemu) or force_config_:
                self._init_web_app_with_token(token, force_config_)
            if not self._local_jemu:
                self._add_event({'event': 'start run'})

            user_os = sys.platform

            if os.name == 'nt' and self._uart_device is True:
                raise VlabException("uart_device option is currently not supported on Windows.", 1)

            # delete self key
            args.pop('self', None)
            # send flags events
            self._add_event({'event': 'jumper run', 'labels': args})

            self._examples_hash_map = self._load_example_hash_map()

        except (VlabException, KeyboardInterrupt) as e:
            if self._jemu_connection:
                self._jemu_connection.close()
            self.stop()
            raise e

    def _load_example_hash_map(self):
        try:
            return json.load(open(self._EXAMPLES_HASH_FILE))
        except Exception as e:
            print(e.message)
            return {}

    def _add_error_event(self, error, extra_labels=None):
        labels = {'error': error}
        if extra_labels:
            labels.update(extra_labels)
        self._add_event({'event': 'error', 'labels': labels})

    def _unsupported_instruction_callback(self, jemu_packet):
        DESCRIPTION = "description"
        ERROR = "error"
        UNIMPLEMENTED_INSTRUCTION = "unimplemented_instruction"
        ASSEMBLY_INSTRUCTION = "assembly_instruction"
        if DESCRIPTION in jemu_packet \
                and jemu_packet[DESCRIPTION] == ERROR and ERROR in jemu_packet and\
                jemu_packet[ERROR] == UNIMPLEMENTED_INSTRUCTION:
                    self._add_error_event('unimplemented instruction', {'instruction': jemu_packet[ASSEMBLY_INSTRUCTION]})

    def _add_event(self, message):
        if not self._local_jemu:
            self._analytics.add_event(message)

    def _send_stop_after_event(self):
        self._add_event({'event': 'jumper run', 'labels': {'parameter': 'stop_after'}})

    def _init_web_app_with_token(self, token, no_browser):
        secret_token = token
        if not secret_token:
            try:
                secret_token = get_token()
            except MissingFileError:
                print('This is the first time your running Jumper on this machine.')
                print('Only this one time, please press enter and follow the instructions in the browser window.')
                from builtins import input
                input("Press enter to continue: ")
                secret_token = login(no_browser)
                input("Press enter to run your firmware!: ")

        try:
            self._web_api = JemuWebApi(jumper_token=secret_token, local_jemu=self._local_jemu)
            self._analytics = Analytics(self._web_api, local_jemu=self._local_jemu)
            self._user_error_reporting.set_web_api(self._web_api)
            self._user_error_reporting.set_analytics(self._analytics)
        except requests.ConnectionError as e:
            raise VlabException("Could not connect to server: " + e.message, 7)

    @staticmethod
    def _silent_remove_file(filename):
        try:
            if os.path.isfile(filename):
                os.remove(filename)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise

    def _valid_file_existence(self, file_path):
        if not os.path.isfile(file_path):
            raise MissingFileError("Failed to open binary file (at: '" + file_path + "')")

    @property
    def uart(self):
        """
        The main UART device for the Virtual Lab session

        :return: :class:`~jumper.jemu_uart.JemuUart`
        """
        return self._uart

    @property
    def gpio(self):
        return self._jemu_gpio

    @property
    def interrupts(self):
        return self._jemu_interrupt

    def _set_uarts_to_print(self):
        if (self._print_uart):
            peripheral_found = False      
            # If the list is empty - turn on all the uarts
            if len(self._uarts_to_print) == 0:
                for component in self._components:
                    if component["type"] == 'uart':
                        component["obj"].print_uart_to_screen()
            
            # The list is not empty - turn on only the relevant uarts to print to screen
            else:
                for uart_name in self._uarts_to_print:
                    for component in self._components:
                        if component["type"] == 'uart' and component["name"] == uart_name:
                            peripheral_found = True
                            component["obj"].print_uart_to_screen()

                    if not peripheral_found:
                        print("Warning - " + uart_name + " is not exist in the uarts of this mcu")
                        
                    # Initialize for the next uart    
                    peripheral_found = False

    def _build_components_methods(self):
        bsp_json = os.path.join(self._working_directory, "bsp.json")
        board_json = os.path.join(self._working_directory, "board.json")
        json_file = None
        bsp_json_parser = JemuBspParser()
        use_default_board = False

        # Use board.json (first priorioty)
        if os.path.isfile(board_json):
            if self._platform:
                print("Notice: 'board.json' exists so '--platform' flag will be ignored if exist")
            self._platform = bsp_json_parser.get_platform(board_json)
            json_file = board_json
        # Use bsp.json    
        elif os.path.isfile(bsp_json):
            if self._platform:
                print("Notice: 'bsp.json' exists so '--platform' flag will be ignored if exist")
            self._platform = bsp_json_parser.get_platform(bsp_json)
            json_file = bsp_json
        # No json file - use platform from the jumper command
        else:
            use_default_board = True
            if self._platform:
                if self._platform not in platforms_list_lower:
                 raise VlabException("platform: {} is not supported".format(self._platform), 7)
            # No platform - use default platform (nrf52832)
            else:
                self._platform = "nrf52832"
            
        default_json = platforms_default_config_dict[self._platform]
        print(default_json)
        if (use_default_board):
            json_file = default_json

        components_list = bsp_json_parser.get_components(self._jemu_connection, json_file)
        components_list = components_list + bsp_json_parser.get_internal_components(default_json, self, self._platform, self._jemu_connection, self._gdb_mode)

        for component in components_list:
            setattr(self, component["name"], component["obj"])

        self._components = components_list

    @staticmethod
    def _get_file_signature(file_path):
        sha1 = hashlib.sha1()

        with open(file_path, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha1.update(data)

        return sha1.hexdigest()

    def load(self, file_path):
        """
        Loads firmware to a virtual device and initialises a Virtual Lab session.
        Use :func:`~jumper.Vlab.start()` to start an emulation after this method was called.

        :param file_path: Path for a firmware file (supported extensions are bin, out, elf, hex)
        """
        ext = [".bin", ".out", ".elf", ".hex"]
        if not file_path.endswith(tuple(ext)):
            self._raise_file_extension_error()

        self._firmware = os.path.abspath(file_path)
        self._valid_file_existence(self._firmware)
        self._new_signature = self._get_file_signature(self._firmware)
        self._prepare_firmware()
        # if not self._is_pu():
        #     self._upload_firmware()

    def _upload_firmware(self):
        if not self._local_jemu:
            firmware = self._firmware
            bsp_json = os.path.join(self._working_directory, "bsp.json")
            board_json = os.path.join(self._working_directory, "board.json")
            scenario_json = os.path.join(self._working_directory, "scenario.json")
            zip_filename = os.path.basename(self._firmware) + '.zip'
            zip_filepath = os.path.join(self._working_directory_dot_jumper, zip_filename)

            with zipfile.ZipFile(zip_filepath, 'w') as myzip:
                myzip.write(firmware, os.path.basename(firmware))
                if os.path.isfile(board_json):
                    myzip.write(board_json, os.path.basename(board_json))
                if os.path.isfile(bsp_json):
                    myzip.write(bsp_json, os.path.basename(bsp_json))
                if os.path.isfile(scenario_json):
                    myzip.write(scenario_json, os.path.basename(scenario_json))

            self._web_api.upload_firmware(zip_filepath, self._user_error_reporting)

    def _file_supported_in_jemu(self):
        if self._firmware.endswith('.bin') or self._firmware.endswith('.hex'):
             return True
        return False

    def _prepare_firmware(self):
        if (not self._file_supported_in_jemu()):
            self._program_file = os.path.join(self._working_directory_dot_jumper, 'program.bin')
            self._generate_program_bin()
        else:
            self._program_file = self._firmware  

    def _generate_program_bin(self):
        filename = os.path.basename(self._firmware)
        if self._new_signature in self._examples_hash_map:
            self._add_event({
                'event': 'upload firmware',
                "labels": {
                    'example': True,
                    'example_name': self._examples_hash_map[self._new_signature],
                    'filename': filename
                }
            })
        else:
            self._add_event({'event': 'upload firmware', "labels": {'example': False, 'filename': filename}})

        source_type = None
        if filename.endswith('.elf') or filename.endswith('.out'):
            source_type = 'elf32-little'
            args = [OBJCOPY_PATH, '-I', source_type, '-I', source_type, self._firmware, self._program_elf]
            subprocess.check_call(args)
        else:
            self._raise_file_extension_error()

        args = [OBJCOPY_PATH, '-I', source_type, '-O', 'binary', self._firmware, self._program_file]
        subprocess.check_call(args)


    @staticmethod
    def _raise_file_extension_error():
        raise ArgumentError('Invalid file extension - supported extensions are bin, out, elf, hex')

    def _get_jemu_port(self):
        @timeout(5)
        def wait_for_file():
            while not os.path.exists(self._jemu_port_file):
                sleep(0.1)

        try:
            wait_for_file()
        except TimeoutException:
            raise EmulationError('Could not connect to emulator. Waiting for port file timed out')

        with open(self._jemu_port_file, 'r') as f:
            return int(f.read().strip())

    def _remove_port_file(self):
        if os.path.exists(self._jemu_port_file):
            os.remove(self._jemu_port_file)

    def start(self, ns=None):
        """
        Starts the emulation

        :param ns: If provided, commands the virtual device to run for the amount of time given in ns and then halt.

            If this parameter is used, this function is blocking until the virtual devices halts,
            if None is given, this function is non-blocking.
        """
        sys.stdout.write('Loading virtual device\n')
        sys.stdout.flush()

        if self._gdb_mode:
            print('Please connect GDB client on port 5555 to continue.\n')

        if not os.path.isfile(JEMU_PATH):
            raise MissingFileError(JEMU_PATH + ' is not found')
        elif not os.access(JEMU_PATH, os.X_OK):
            raise MissingFileError(JEMU_PATH + ' is not executable')

        self._remove_pty_if_exist()
        self._remove_port_file()
        self._was_start = True

        jemu_cmd = self._build_jemu_cmd()
        self._user_error_reporting.set_jemu_cmd(jemu_cmd)

        def jemu_connection():
            @timeout(6)
            def wait_for_connection(port):
                self._logger.debug('wait_for_connection(port)')
                while not self._jemu_connection.connect(port):
                    sleep(0.1)

            try:
                port = self._get_jemu_port()
                wait_for_connection(port)
            except TimeoutException:
                self._logger.debug('wait_for_connection(port) timed out')
                self.stop()
                raise EmulationError(
                    "Error: Couldn't connect to Emulator. Please contact us at support@jumper.io with a copy of this trace text"
                )
            self._jemu_gpio.set_connection_manager(self._jemu_connection)
            self._jemu_interrupt.set_jemu_connection(self._jemu_connection)
            self._user_error_reporting.set_jemu_connection(self._jemu_connection, self._local_jemu)
            self._jemu_connection.register(self.receive_packet)

            if not self._jemu_connection.start():
                raise EmulationError(
                    "Error: Couldn't connect to Emulator. Please contact us at support@jumper.io with a copy of this trace text"
                )

        if self._jemu_debug:
            # This is here for supporting python <2.7 in production
            from builtins import input

            input("Start a debugger with the following parameters:\n\
            cwd: {}\n\
            command: {}\n\
            Press Enter to continue...".format(self._working_directory, ' '.join(jemu_cmd))
                  )
        else:
            try:
                self._jemu_process = subprocess.Popen(
                    jemu_cmd,
                    cwd=self._working_directory,
                    stdin=subprocess.PIPE,
                    env=SSL_ENV
                )

                if self._debug_peripheral:
                    # This is here for supporting python <2.7 in production
                    from builtins import input

                    input("In order to debug your peripheral attach to process"
                          " pid: {}\nPress enter after connection...".format(self._jemu_process.pid))
                sleep(0.3)
            except Exception as e:
                raise EmulationError(e.message)

        jemu_connection()

        exiter = threading.Thread(target=self._exiter_loop)
        self._threads.append(exiter)
        exiter.start()

        try:
            self._open_uarts()
        except TimeoutException:
            self.stop()
            raise EmulationError("Error: Uart doesn't exist. Please contact us at support@jumper.io with a copy of this trace text")

        if ns is not None:
            self.run_for_ns(ns)
        else:
            self.SUDO.resume()

    def _open_uarts(self):
        for component in self._components:
            if component["type"] == 'uart':
                component["obj"].open()

    
    def _exiter_loop(self):
        while self.is_running():
            sleep(0.5)
        with self._exit_lock:
            if self._on_exit:
                self._on_exit(self.SUDO.get_exit_code(), self._error_string)

    def register_on_exit(self, callback):
        with self._exit_lock:
            self._on_exit = callback

    def _aggregate_traces(self):
        traces = []
        if self._registers_trace:
            traces.append('regs')
        if self._functions_trace:
            traces.append('functions')
        if self._interrupts_trace:
            traces.append('interrupts')
        return traces

    def _build_jemu_cmd(self):
        jemu_cmd = [JEMU_PATH, '-w', '--sdk-port', str(self._jemu_port)]

        jemu_cmd.append('-i')
        jemu_cmd.append(self._program_file)

        if self._gpio_flag:
            jemu_cmd.append('--gpio')
        if self._gdb_mode:
            jemu_cmd.append('-g')
        if self._sudo_mode:
            jemu_cmd.append('-s')

        if self._stack_max_:
            jemu_cmd.append('--sp')

        if self._platform:
            jemu_cmd.append('--mcu')
            jemu_cmd.append(self._platform)

        if self._code_coverage:
            jemu_cmd.append('--code-coverage')

        if self._mips:
            jemu_cmd.append('--mips')

        if 'functions' in self._traces:
            self._build_obj_dump_file(jemu_cmd)

        traces_string = ','.join(self._traces) if len(self._traces) > 0 else None
        if traces_string:
            jemu_cmd.extend(['-t', traces_string])

        if self._trace_output_file:
            jemu_cmd.append('--trace-dest')
            jemu_cmd.append(self._trace_output_file)

        if self._print_uart:
            # print uart to file - jemu responsible
            if self._uart_output_file:
                full_file_arg = "file:" + self._uart_output_file
                jemu_cmd.append('--uart_output={}'.format(full_file_arg))

        if self._uart_device:
            jemu_cmd.append('-y')

        if self._is_pu():
            jemu_cmd.append('--pu')

        return jemu_cmd

    def _is_pu(self):
        return False if not self._web_api else self._web_api.is_pu()

    def _build_obj_dump_file(self, jemu_cmd):
        if not self._firmware.endswith('.out') and not self._firmware.endswith('.elf'):
            raise ArgumentError('Invalid file extension - for running functions trace, use out or elf file')

        # create dump file
        objdump_file = os.path.join(self._working_directory_dot_jumper, 'objdump.txt')
        try:
            args = [OBJDUMP_PATH, '-d', self._firmware]
            output = subprocess.check_output(args)
            with open(objdump_file, 'w') as f:
                f.write(output)
        except Exception as e:
            raise EmulationError(e.message)

        jemu_cmd.extend(['--objdump', objdump_file])

    def stop(self):
        """
        Stops the Virtual Lab session.

        Opposing to halting the session, the virtual device cannot be resumed after a stop command.

        """
        # amir removed this
        #if self._jemu_connection:
         #   self._jemu_connection.close()
        self._logger.debug('stop()')
        self._uart = None
        self._jemu_connection = None

        if self._jemu_process and self._jemu_process.poll() is None:
            if os.name == 'nt':  # win
                os.kill(self._jemu_process.pid, signal.SIGTERM)
            else:
                self._jemu_process.terminate()

            @timeout(5)
            def try_wait():
                self._logger.debug('waiting for jemu_process')
                self._jemu_process.wait()
                self._logger.debug('done waiting for jemu_process')

            try:
                try_wait()
            except TimeoutException:
                self._logger.debug('waiting for jemu_process timed out. Killing')
                self._jemu_process.kill()
                # self._jemu_process.wait()

        elif self._jemu_debug:
            from builtins import input
            input("Press enter when the process is closed...")

        self._stop_threads()

        if self._analytics:
            self._analytics.stop()

        if self._web_api:
            self._web_api.stop()

        self._remove_pty_if_exist()

    def _stop_threads(self):
        for t in self._threads:
            if t.is_alive() and (get_ident() != t.ident):
                t.join()

    def _remove_pty_if_exist(self):
        possible_uart_files = ['uart', 'USART1', 'USART2', 'USART6']
        for filename in possible_uart_files:
            uart_device_path = os.path.join(self._working_directory, filename)
            if not os.path.exists(uart_device_path):
                continue

            if not os.path.islink(uart_device_path):
                raise Exception(uart_device_path + ' not symbolic link')

            os.unlink(uart_device_path)

    def run_for_ms(self, ms):
        """
        Starts or resumes the virtual device, the device will halt after the amount of time specified.

        This function is blocking until the virtual device has halted. Use this when the virtual device is stopped
        or halted.

        :param ms: Time to run in ms
        """
        self.run_for_us(ms * 1000)

    def run_for_us(self, us):
        """
        Starts or resumes the virtual device, the device will halt after the amount of time specified.

        This function is blocking until the virtual device has halted. Use this when the virtual device is stopped
        or halted.

        :param ms: Time to run in us
        """
        self.run_for_ns(us * 1000)

    def run_for_ns(self, ns):
        """
        Starts or resumes the virtual device, the device will halt after the amount of time specified.

        This function is blocking until the virtual device has halted. Use this when the virtual device is stopped
        or halted.

        :param ns: Time to run in ns
        """
        if not self._was_start:
            self.start(ns)
        else:
            self.SUDO.run_for_ns(ns)

    def stop_after_ms(self, ms):
        # """
        # Causes the virtual device to halt after the amount of time specified.
        # This function is non-blocking and does not cause the device to resume.
        #
        # Use this when the virtual device is halted.
        #
        # :param ms: Time to run in ms
        # """
        self.stop_after_ns(ms * 1000000)

    def stop_after_ns(self, ns):
        # """
        # Causes the virtual device to halt after the amount of time specified.
        # This function is non-blocking and does not cause the device to resume.
        #
        # Use this when the virtual device is halted.
        #
        # :param ns: Time to run in ns
        # """
        self.SUDO.stop_after_ns(ns)

    def resume(self):
        """
        Resumes a paused device.

        """
        self.SUDO.resume()

    def cancel_stop(self):
        self.SUDO.cancel_stop()

    def pause(self):
        """
        Pause the device.

        """
        self.SUDO.pause()

    def on_interrupt(self, callback):
        """

        :param callback: The callback to be called when an interrupt is being handled. The callback will be called with callback(interrupt)
        """
        self._jemu_interrupt.on_interrupt([callback])

    def set_timer(self, ns, callback):
        self.SUDO.set_timer(ns, callback)

    def get_state(self):
        if not self._was_start:
            return "init"
        elif not self.is_running():
            return "stopped"
        try:
            return self.SUDO.get_state()
        except JemuConnectionException:
            return 'stopped'

    def on_uart_read_line(self, callback):
        """
        Specifies a callback for a uart read line.

        :param callback: The callback to be called when a line exist in the buffer. The callback will be called with callback(line)
        """
        self.uart.on_uart_read_line(callback)

    def on_pin_level_event(self, callback):
        """
        Specifies a callback for a pin transition event.

        :param callback: The callback to be called when a pin transition occures. The callback will be called with callback(pin_number, pin_level, time)
        """
        self.gpio.on_pin_level_event(callback)

    def get_pin_level(self, pin_num):
        """
        Specifies get the pin level for a pin num.

        :param pin num: pin number id
        """
        return self.gpio.get_pin_level(pin_num)

    def on_bkpt(self, callback):
        """
        Sets a callback to be called when the virtual device execution reaches a BKPT assembly instruction.

        :param callback: The callback to be called. Callback will be called with callback(code)\
        where code is the code for the BKPT instruction.
        """
        self._on_bkpt = callback

    def receive_packet(self, jemu_packet):
        if jemu_packet[self._DESCRIPTION] == self._BKPT:
            if self._on_bkpt is not None:
                bkpt_code = jemu_packet[self._VALUE_STRING]
                self._on_bkpt(bkpt_code)
        elif jemu_packet[self._DESCRIPTION] == self._ERROR:
            self._error_string = jemu_packet[self._VALUE_STRING]

    def is_running(self):
        """
        Checks if the virtual device has been started.

        :return: True if running or paused, False otherwise.
        """
        if self.SUDO.get_exit_code() is not None:
            return False

        if not self._jemu_process:
            if self._jemu_debug:
                return True
            else:
                return False

        return self._jemu_process.poll() is None

    def _raise_jemu_process_for_failure(self):
        if self._jemu_process is None:
            return

        jemu_exit_code = self._jemu_process.poll()
        if jemu_exit_code not in [None, 0, signal.SIGTERM]:
            raise EmulationError("jemu exited with a non-zero exit code: {}".format(jemu_exit_code))

    def get_return_code(self):
        """
        Checks a return code from the device.
        Raises EmulationError if a failure occured during execution

        :return:
            - 0 if device was stopped using the :func:`~stop()` method
            - Exit code from firmware if the Device exited using the jumper_sudo_exit_with_exit_code() \
            - None if the virtual device is still running command from jumper.h
        """
        self._raise_jemu_process_for_failure()
        sudo_exit_code = self.SUDO.get_exit_code()
        return sudo_exit_code if sudo_exit_code is not None else 0

    def _assert_jemu_is_running(self):
        if not self.is_running():
            raise EmulationError("Error: The Emulator is not running.")

    def get_device_time_ns(self):
        """
        How much time passed from beginning of the emulation.

        :return: Emulation time in nanoseconds.
        """
        return self.SUDO.get_device_time_ns()

    def get_device_time_us(self):
        """
        How much time passed from beginning of the emulation.

        :return: Emulation time in microseconds.
        """
        return self.get_device_time_ns() / 1000

    def get_device_time_ms(self):
        """
        How much time passed from beginning of the emulation.

        :return: Emulation time in milliseconds.
        """
        return self.get_device_time_us() / 1000

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *err):
        self._add_event({'event': 'stop run'})
        self.stop()

    def __del__(self):
        self.stop()

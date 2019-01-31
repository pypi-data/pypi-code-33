import re
import sys
from .common import VlabException
from .vlab import Vlab
from threading import Event
import logging


def init_vlab(args):
    registers_trace = False
    functions_trace = False
    interrupts_trace = False
    uarts_to_print = []
    if args.traces_list:
        for trace in args.traces_list.split(','):
            if trace == 'registers' or trace == 'regs':
                registers_trace = True
            elif trace == 'functions':
                functions_trace = True
            elif trace == 'interrupts':
                interrupts_trace = True
            else:
                raise VlabException(
                    'jumper run: error: Invalid trace type {}. Valid traces are regs, functions, interrupts'.format(
                        trace), 1)

    # print-uart can be True/False, or list of uarts.
    # In case it's a list of uarts (type is str), it is needed to save the uarts and set the print-uart to true
    if type(args.print_uart) is str:
        uarts_to_print = args.print_uart.split(',')
        args.print_uart = True

    vlab = Vlab(
        working_directory=args.working_directory,
        sudo_mode=args.sudo_mode,
        gdb_mode=args.gdb_mode,
        registers_trace=registers_trace,
        functions_trace=functions_trace,
        interrupts_trace=interrupts_trace,
        trace_output_file=args.trace_output_file,
        print_uart=args.print_uart,
        uarts_to_print = uarts_to_print,
        uart_output_file=args.uart_output_file,
        uart_device=args.uart_device,
        platform=args.platform,
        token=args.token,
        debug_peripheral=args.debug_peripheral,
        gpio=args.gpio,
        stack_max=args.stack_max,
        code_coverage=args.code_coverage,
        print_mips=args.mips
    )

    vlab.load(args.fw)

    return vlab


def stop_after_parse(stop_after):
    def raise_invalid_time():
        print('Invalid time format for --stop-after: {}'.format(stop_after))
        return None

    match = re.match('^\d+',stop_after)
    if not match:
        return raise_invalid_time()
    ns = int(match.group(0))

    if re.match('^\d+$', stop_after) or re.match('^\d+ms$', stop_after):
        ns = ns * 1000 * 1000
    elif re.match('^\d+s$', stop_after):
        ns = ns * 1000 * 1000 * 1000
    elif re.match('^\d+us$', stop_after):
        ns = ns * 1000
    elif re.match('^\d+ns$', stop_after):
        pass
    else:
        return raise_invalid_time()

    return ns


class VlabRunner:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.WARNING)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self._logger.addHandler(handler)
        self.stop = Event()
        self.stop.clear()
        pass

    def _exit_callback(self, error_code, error_msg):
        # error_code & error_msg not it use here, but part of callback interface
        self.stop_run()

    def start(self, args):
        self._logger.debug('start')
        try:
            def bkpt_callback(code):
                print('Firmware reached a BKPT instruction with code {}'.format(code))
                self.stop.set()

            vlab = init_vlab(args)
            vlab.on_bkpt(bkpt_callback)
            vlab.register_on_exit(self._exit_callback)
            ns = None

            if args.stop_after:
                vlab._send_stop_after_event()

                ns = stop_after_parse(args.stop_after)
                if ns is None:
                    return 1

            try:
                self._logger.debug('vlab.start(0)')
                vlab.start(0)  # stop after 0 millisecond
                self._logger.debug('vlab.start(0) returned')
                if not args.print_uart and not args.traces_list:
                    print(
                        '\nVirtual device is running without UART/Trace prints (use -u and/or -t to get your firmware '
                        'execution status)\n')
                else:
                    print('\nVirtual device is running.\n')
                    sys.stdout.flush()

                if ns:
                    self._logger.debug('vlab.SUDO.set_timer(ns, self.stop_run)')
                    vlab.SUDO.set_timer(ns, self.stop_run)

                self._logger.debug('resume()')
                vlab.resume()
                self._logger.debug('resume() returned')
            except VlabException:
                pass

            self.wait_to_finish()

            self._logger.debug('Stop')
            vlab.stop()
            self._logger.debug('get return code')
            return vlab.get_return_code()

        except VlabException as e:
            print('jumper run: error: {}'.format(e.message))
            try:
                if vlab:
                    vlab.stop()
            finally:
                return e.exit_code

    def stop_run(self):
        self._logger.debug('stop_run()')
        self.stop.set()

    def wait_to_finish(self):
        self._logger.debug('wait_to_finish()')
        while not self.stop.wait(timeout=0.1):
            pass
        self._logger.debug('wait_to_finish done')

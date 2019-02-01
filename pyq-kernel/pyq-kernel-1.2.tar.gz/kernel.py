from __future__ import print_function, absolute_import

import getopt
import json
import os
import shutil
import sys
import tempfile

from ipykernel.eventloops import register_integration
from ipykernel import version_info as ipk_version
from ipykernel.ipkernel import IPythonKernel
from ipykernel.kernelapp import IPKernelApp
from pyq import q, kerr


MIN_PORT = 1024
MAX_PORT = 65535
app = None


class Kernel(IPythonKernel):

    def do_shutdown(self, restart):
        q('\\t 0')
        q('\\p 0')
        return IPythonKernel.do_shutdown(self, restart)


def kernel_spec():
    executable = os.getenv('QBIN')
    prefix = os.path.realpath(sys.prefix)
    script = os.path.join(prefix, "q", "pyq-kernel.p")
    spec = {
        "argv": [executable, script, str(MIN_PORT), str(MAX_PORT), "{connection_file}", ],
        "display_name": "PyQ %d" % sys.version_info[0],
        "language": "python"
    }
    env = {}
    for name in ['QHOME', 'QLIC', 'CPUS']:
        value = os.getenv(name)
        if value is not None:
            env[name] = value
    if env:
        spec['env'] = env
    return spec


def install_kernel_spec(name, user, prefix):
    from jupyter_client.kernelspec import KernelSpecManager
    ksm = KernelSpecManager()
    spec = kernel_spec()
    td = tempfile.mkdtemp()
    try:
        os.chmod(td, 0o755)
        with open(os.path.join(td, 'kernel.json'), 'w') as f:
            json.dump(spec, f, sort_keys=True, indent=4)
            f.write('\n')
        with open(os.path.join(td, 'logo-64x64.svg'), 'wb') as f:
            f.write(LOGO)
        print('Installing "%(display_name)s" kernel spec.' % spec)
        ksm.install_kernel_spec(td, name, user=user, prefix=prefix)
    finally:
        shutil.rmtree(td)


if ipk_version < (5, 0):
    def i1():
        app.kernel.do_one_iteration()
else:
    import asyncio

    def i1():
        loop = asyncio.get_event_loop()
        loop.call_soon(loop.stop)
        loop.run_forever()


@register_integration('q')
def loop_q(kernel):
    q.i1 = i1
    q('.z.ts:{@[i1;();::]}')
    poll_interval = int(0.7 * 1000 * kernel._poll_interval)
    q('\\t %s' % poll_interval)


def is_root():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False  # assume not an admin on non-Unix platforms


def main(argv):
    name = 'pyq_%d' % sys.version_info[0]
    prefix = None
    user = not is_root()

    opts, _ = getopt.getopt(argv, '', ['user', 'prefix=', 'min-port=', 'max-port='])
    for k, v in opts:
        if k == '--user':
            user = True
        elif k == '--prefix':
            prefix = v
            user = False
        elif k == '--name':
            name = v
        elif k == '--min-port':
            global MIN_PORT
            MIN_PORT = int(v)
        elif k == '--max-port':
            global MAX_PORT
            MAX_PORT = int(v)

    install_kernel_spec(name, user, prefix)


def start():
    global app
    app = IPKernelApp.instance(kernel_class=Kernel)
    args = [str(a) for a in q('.z.x')]
    app.initialize(['-f', args[-1]])
    app.shell.enable_gui('q')
    app.shell.extension_manager.load_extension('pyq.magic')
    app.kernel.start()
    loop_q(app.kernel)
    min_port, max_port = map(int, args[:2])
    for port in range(min_port, max_port + 1):
        try:
            q('\\p %d' % port)
        except kerr:
            pass
        else:
            break


LOGO = b"""\
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd" >
<svg version="1.0"
     xmlns="http://www.w3.org/2000/svg"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     viewBox="-1000 -850 2000 2000"
     preserveAspectRatio="xMidYMid meet">
    <defs>
        <g id="Letter-Y">
            <path d="M0 0
        l133 -256h-47v-76h178v76h-53l-170 328v271h48v75h-178v-75h47v-271l-179 -328h-43v-76
        h178v76h-47
        z"/>
        </g>
        <g id="Letter-q">
            <path d="M0 0
        v-341h-186c-17 0 -30 15 -30 33v276c0 17 13 32 30 32h186z
        M-2 80
        h-209c-52 0 -95 -40 -95 -88v-324c0 -48 43 -88 95 -88h339v79h-50v596h50v75h-178v-75h48v-175
        z"/>
        </g>
    </defs>

    <circle cx="0" cy="150" r="1000" fill="#1A3A57" stroke="none"/>
    <path d="M600 750 a 1000 1000 0 0 0 -1200 0" fill="orange"/>
    <use xlink:href="#Letter-q"
         fill="#e1e4e5" stroke="#e1e4e5" stroke-width="20"
         stroke-linejoin="round"
         transform="scale(-1, 1) translate(600, 300) rotate(15)"/>

    <use xlink:href="#Letter-Y"
         fill="#e1e4e5" stroke="#e1e4e5" stroke-width="20"
         stroke-linejoin="round"/>

    <use xlink:href="#Letter-q"
         fill="#e1e4e5" stroke="#e1e4e5" stroke-width="20"
         stroke-linejoin="round"
         transform="translate(600, 300) rotate(15)"/>
</svg>
"""

if __name__ == '__main__':

    if len(sys.argv) < 2 or sys.argv[1] != 'install':
        print("""\
Usage: pyq -mpyq.kernel install [options]

    Options:

       --user - user install;
       --prefix=<dir> - system install in dir;
       --min-port=<port> - minimal port to try for the kdb+ server;
       --max-port=<port> - largest port to try for the kdb+ server.
""")
    else:
        main(argv=sys.argv[2:])

# -----------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2018 Luzzi Valerio for Gecosistema S.r.l.
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# Name:        execution
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     27/07/2018
# -----------------------------------------------------------------------------
import os,sys,ast
import subprocess
from .strings import *
from .filesystem import *
from .platform import *
import datetime

def Exec(command, env={}, precond=[], postcond=[], remove=[], skipIfExists=False, nowait=False, verbose=False, outputmode="boolean"):
    """
    Exec
    """
    t1 = datetime.datetime.now()
    res = True
    outdata = False

    if skipIfExists:
        # check post conditions
        for filename in postcond:
            if not os.path.isfile(filename):
                res = False
                break
        if res:
            t2 = datetime.datetime.now()
            if verbose:
                command = sformat(command, env)
                print("Post conditions already fulfilled for %s[...]!" % command[:80])
                print("Done in %ss." % ((t2 - t1).total_seconds()))
            return True if outputmode=="boolean" else {"success":True}

    res = True
    # check pre conditions (file existence)
    for filename in listify(precond):
        if not os.path.isfile(filename):
            res = False
            break
    if verbose:
        print(sformat(command, env))
    if res:

        if isWindows():
            command = sformat(command, env)
            args = command
        else:
            command = command.replace('"{', '{').replace('}"', '}')
            command = sformat(command, env)
            command = normalizestring(command)
            args = listify(command, " ", '"')
        if nowait:
            p = subprocess.Popen(args, stdout=subprocess.PIPE)
            outdata = p.communicate()
        else:
            try:
                #subprocess.call(args, shell=False)
                with open(os.devnull, 'w') as devnull:
                    outdata = subprocess.check_output(command, stderr=devnull).decode('utf-8')
                    if outputmode=="json":
                        if "[" in outdata or "{" in outdata:
                            outdata = ast.literal_eval(outdata)

            except subprocess.CalledProcessError as e:
                print("Exec:",e)
                if outputmode=="boolean":
                    return False
                else:
                    return {"success":False,"exception":""+e.output, "returncode":e.returncode}

    # check post conditions
    for filename in listify(postcond):
        if verbose:
            print("Checking post conditions:%s" % filename)
        if not os.path.isfile(filename):
            res = False
            break
    # remove temporary files
    for filename in listify(remove):
        if verbose:
            print("removing temp file:%s" % filename)
        if os.path.isfile(filename):
            os.remove(filename)
    t2 = datetime.datetime.now()
    if verbose:
        print("Done in %ss." % ((t2 - t1).total_seconds()))
    return res if outputmode=="boolean" else {"success":res,"data":outdata}

def EXEC(command):
    """
    shortcut for Exec
    """
    return Exec(command)

def Python(command, env={}, precond=[], postcond=[], remove=[], skipIfExists=False, verbose=False, outputmode="boolean"):
    """
    Python
    """
    filetmp=""
    PYTHON_HOME = env["PYTHON_HOME"] +"/" if "PYTHON_HOME" in env else ""

    if isstring(command) and not isfile(command):
        filetmp = tempfname(ext="py")
        strtofile(command,filetmp)
        command = filetmp

    if verbose:
        print(PYTHON_HOME + "python " +command)
    return Exec(PYTHON_HOME + "python " + command, env, precond, postcond, remove=[filetmp], skipIfExists=skipIfExists, nowait=False, verbose=verbose, outputmode=outputmode)

def Python36(command):
    """
    Python36
    """
    env ={"PYTHON_HOME":"c:/Python36"}
    return Python(command,env,outputmode="json")


def PYTHON(command):
    """
    PYTHON
    """
    return Python(command,verbose=True,outputmode="boolean")

def Rscript(command, additional_lib="", verbose=False):
    """
    Rscript -  call  rscript interpreter
    """

    command = """Rscript --vanilla %s""" % (command)
    if verbose:
        print(command)
    environ = os.environ
    environ['R_LIBS_USER'] = additional_lib
    p = subprocess.Popen(command, env=environ, stdout=subprocess.PIPE)

    res = p.communicate()
    res = [item for item in res if item]
    res = res[0].split("\r\n") if len(res) > 0 else []
    res = [item.strip("[1] ") for item in res if item]
    if verbose:
        for item in res:
            print( "-->" + item)
    res = res[-1] if len(res) > 0 else ""
    return res
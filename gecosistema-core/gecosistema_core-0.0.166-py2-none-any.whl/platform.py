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
# Name:        platform
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     27/07/2018
# -----------------------------------------------------------------------------
import os,sys,time
import multiprocessing

def cpu_count():
    """
    cpu_count
    """
    return multiprocessing.cpu_count()

def isWindows():
    """
    isWindows
    """
    return os.name == "nt" or sys.platform.startswith("win")

def isLinux():
    """
    isLinux
    """
    return sys.platform.startswith("linux")

def isMac():
    """
    isMac
    """
    return sys.platform.startswith("darwin")

def Desktop():
    """
    Desktop path
    """
    return os.path.expanduser('~') + "/Desktop"

def Home():
    """
    Home directory
    """
    return os.path.expanduser('~')

def safename(filename, additional_chars=r''):
    """
    safename - give a safe name for the filesystem
    """
    if isWindows():
        notallowed = r'~"#%&*:<>?{|}'
    elif isLinux():
        notallowed = r''
    elif isMac():
        notallowed = r':'

    chars = notallowed + additional_chars
    for j in range(len(chars)):
        c = chars[j]
        filename = filename.replace(c,'_')

    return filename

def pause():
    """
    pause
    """
    os.system("pause")

def sleep(s):
    """
    sleep
    """
    time.sleep(s)

def setenv(varname, value):
    """
    setenv
    """
    os.environ[varname] = value

def add_site_packages(pathname):
    """
    addpath
    """
    if not pathname in sys.path:
        sys.path.append(pathname)

if __name__ == '__main__':
    workdir = r"D:\Users\vlr20\Projects\BitBucket\OpenSITUA\apps\common\lib\js\corex"
    chdir(workdir)
    filename= "hello.txt"
    print(safename(filename))
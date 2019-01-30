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
# Name:        xml_utils
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     13/08/2018
# -----------------------------------------------------------------------------
from .strings import *
from .filesystem import *
import json
from xmljson import yahoo as bf
from xml.etree.ElementTree import fromstring


def parsejson(filename):
    """
    parsejson
    """
    if isinstance(filename, (dict)):
        return filename
    elif isfile(filename):
        text = filetostr(filename)
    elif isstring(filename):
        text = filename
    else:
        return {}
    return json.loads(text)

# -------------------------------------------------------------------------------
#   parsexml
# -------------------------------------------------------------------------------
def parsexml(filename, patching=True):
    """
    parsexml
    """
    if isinstance(filename, (dict)):
        return filename
    elif isstring(filename) and filename.startswith("<"):
        text = filename
    elif file(filename):
        text = filetostr(filename)
    else:
        return ""
    # patch  remove text that could create problems in javascript parsing
    if patching:
        text2remove = textin(text, "![CDATA[", "]]", False)
        text = text.replace(text2remove, "")

        # text = text.replace("&lt;","<")
    # end patch
    data = bf.data(fromstring(text))
    return data

def readmssql(filename):
    """
    readmssql - read xml mssql config connection

    <!DOCTYPE connections>
    <qgsMssqlConnections version="1.0">
        <mssql port="" saveUsername="true" password="12345" savePassword="true" sslmode="1" service="" username="sa" host=".\SQLEXPRESS" database="SearchComboBox" name="MSSQL" estimatedMetadata="true"/>
    </qgsMssqlConnections>
    """
    env = {}
    xml = parsexml(filename)
    if xml:
        conn = xml["qgsMssqlConnections"]["mssql"]
        env["server"] = conn["host"]
        env["uid"] = conn["username"]
        env["pwd"] = conn["password"]
        env["database"] = conn["database"]
        env["catalog"] = "dbo"
        env["tablename"] = conn["name"]
    return env

if __name__ == '__main__':
    workdir = r"D:\Users\vlr20\Projects\BitBucket\OpenSITUA\apps\common\lib\js\corex"
    chdir(workdir)
    filename= "hello.txt"
    print(safename(filename))
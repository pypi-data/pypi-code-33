# -------------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2018 Luzzi Valerio 
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
#
# Name:        math.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     10/10/2018
# -------------------------------------------------------------------------------
import numpy as np

def M(s,o):
    """
    M - 
    s - array of predictions (or simulated)
    o - array of observations (or targets)
    """
    s,o = np.array(s),np.array(o)
    return np.nansum( np.abs( np.divide(s-o,o) ))/len(o)

def MSE(s,o):
    """
    Mean Square Error
    s - array of predictions (or simulated)
    o - array of observations (or targets)
    """
    s, o = np.array(s), np.array(o)
    return np.nanmean((s-o)**2)

def RMSE(s,o):
    """
    Root Mean Square Error
    s - array of predictions (or simulated)
    o - array of observations (or targets)
    """
    s, o = np.array(s), np.array(o)
    return np.sqrt( np.nanmean((s-o)**2) )

def NASH(s,o):
    """
    Nash Sutcliffe
    s - array of predictions (or simulated)
    o - array of observations (or targets)
    """
    s, o = np.array(s), np.array(o)
    return 1.0 - np.nansum( (s-o)**2 ) / np.nansum( (o-np.nanmean(o))**2 )
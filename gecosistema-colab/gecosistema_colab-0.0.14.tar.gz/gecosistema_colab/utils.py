#!/usr/bin/env python
#-*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
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
# Name:        utils.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     10/10/2018
# ------------------------------------------------------------------------------
from google.colab import files
import matplotlib.pyplot as plt
from gecosistema_core import *
from gecosistema_gdal import *


def upload():
    """
    upload
    """
    if files:
        uploaded = files.upload()
        return uploaded.keys()[0]
    return ""

def plot(filename, cmap = plt.cm.summer):
    """
    plot
    """
    if isfile(filename):
        plt.axis('off')
        data,_,_=GDAL2Numpy(filename)
        plt.imshow(data ,cmap=cmap)
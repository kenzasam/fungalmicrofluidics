"""
    This file is part of GSOF_ArduBridge.

    GSOF_ArduBridge is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    GSOF_ArduBridge is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with GSOF_ArduBridge.  If not, see <https://www.gnu.org/licenses/>.
"""
"""
Class to view spectrum from Ocean Optics spectrometer as a thread.
Based on and adapted from SpectrOMat, copyright Tobias Dusa.
"""


__version__ = "1.0.0"

__author__ = "Kenza Samlali"
__copyright__ = "Copyright 2020"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = ""
__status__ = "Production"

import math, time
import sys
import numpy

'''
#import seabreeze
#seabreeze.use('pyseabreeze')
import seabreeze.spectrometers as sb
from sb import Spectrometer, list_devices
'''
try:
    import seabreeze
    seabreeze.use('pyseabreeze')
    import seabreeze.spectrometers as sb
    from sb import Spectrometer, list_devices
except ImportError:
    sb=None

# Plotting
import matplotlib.animation as animation
import matplotlib.pyplot as plot


def openspec(nr):
    devices=list_devices()
    spec= Spectrometer(devices[nr])
    return spec

def acquire(spec, t):
    #setting integration time in microseconds
    spec.integration_time_micros(t)
    # get wavelengths
    wavelengths = spec.wavelengths()
    wavelengths #array output
    # get intensities
    intensities = spec.intensities()
    return intensities  #array output

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
import numpy

'''
#import seabreeze
#seabreeze.use('pyseabreeze')
import seabreeze.spectrometers as sb
from sb import Spectrometer, list_devices
'''
try:
    import seabreeze
    #seabreeze.use('pyseabreeze')
    import seabreeze.spectrometers as sb
    from seabreeze.spectrometers import Spectrometer, list_devices
except ImportError:
    sb=None

# Plotting
import matplotlib.animation as animation
import matplotlib.pyplot as plot

def __init__(self,
            device,
            inttime,
            autoexposure,
            autorepeat,
            autosave,
            dark_frames,
            enable_plot,
            output_file,
            scan_frames,
            scan_time,
            root= None,
            ):
    self.init_device(device=device)

def init_device(self, device='#0'):
    #Initialize spectrometer device
    try:
        if ('SIMULATOR'.startswith(device.upper())):
            self.spec = SBSimulator()
        elif (device == ''):
            #print('allo')
            #self.spec = sb.Spectrometer(sb.list_devices()[int(device[1:])])
            print('No spec serial number listed. Picking first spec found.')
            dev=list_devices()
            self.spec = Spectrometer(dev[0])
        else:
            print('Serial number listed.')
            self.spec = Spectrometer.from_serial_number(device)
    except:
        print('ERROR: Could not initialize device "' + device + '"!')
        if (sb is None):
            print('SeaBreeze library not found!')
        else:
            print('Available devices:')
            index = 0
            for dev in list_devices():
                print(' - #' + str(index) + ':', 'Model:', dev.model + '; serial number:', dev.serial)
                index += 1
        if ('Y'.startswith(input('Simulate spectrometer device instead?  [Y/n] ').upper())):
            self.spec = SBSimulator()
        else:
            sys.exit(1)
    print(self.spec)
    self.wavelengths = self.spec.wavelengths()
    self.samplesize = len(self.wavelengths)
    def init_variables(self,
                       autoexposure=False,
                       autorepeat=False,
                       autosave=True,
                       dark_frames=1,
                       enable_plot=True,
                       output_file='Snapshot-%Y-%m-%dT%H:%M:%S%z.dat',
                       root=None,
                       scan_frames=1,
                       scan_time=100000):
        """Initialize instance variables"""
        self.run_measurement = False
        self.have_darkness_correction = False
        #self.button_startpause_texts = { True: 'Pause Measurement', False: 'Start Measurement' }
        #self.button_stopdarkness_texts = { True: 'Stop Measurement', False: 'Get Darkness Correction' }
        #self.autoexposure = IntVar(value=autoexposure)
        #self.autorepeat = IntVar(value=autorepeat)
        #self.autosave = IntVar(value=autosave)
        #self.dark_frames = StringVar(value=dark_frames)
        #self.enable_plot = IntVar(value=enable_plot)
        #self.output_file = StringVar(value=output_file)
        #self.scan_frames = StringVar(value=scan_frames)
        #self.scan_time = StringVar(value=scan_time)
        #self.timestamp = '%Y-%m-%dT%H:%M:%S%z'
        self.message = StringVar()
        #self.total_exposure = int(scan_frames) * int(scan_time)
        # Initialize variables
        self.darkness_correction = [0.0]*(len(self.spec.wavelengths()))
        self.measurement = 0
        self.data = [0.0]*(len(self.spec.wavelengths()))
def init_plot(self):
    """Initialize plotting subsystem"""
    # Plot setup
    self.figure = plot.figure()
    self.axes = self.figure.gca()
    self.graph, = self.axes.plot(self.wavelengths, self.data)
    self.figure.suptitle('No measurement taken so far.')
    self.axes.set_xlabel('Wavelengths [nm]')
    self.axes.set_ylabel('Intensity [count]')
    #self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)

def update_plot(self,i):
    scan_frames = int(self.scan_frames.get())
    if (self.measurement == scan_frames) or \
       (self.enable_plot.get() > 0):
        self.graph.set_ydata(self.data)
        self.axes.relim()
        self.axes.autoscale_view(True, True, True)
def startplot(self):
    plot_animation= animation.FuncAnimation(self.figure, self.update_plot)

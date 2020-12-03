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
from GSOF_ArduBridge import threadBasic as TB
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
plot_animation= None

class Flame(TB.BasicThread):
    def __init__(self,
                Period,
                nameID,
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
                viewer={}
                ):
        TB.BasicThread.__init__(self, nameID=nameID, Period = Period, viewer=viewer)
        self.T0 = time.time()
        self.init_device(device=device)
        self.init_variables(
                           autoexposure=False,
                           autorepeat=False,
                           autosave=True,
                           dark_frames=1,
                           enable_plot=True,
                           output_file='Snapshot-%Y-%m-%dT%H:%M:%S%z.dat',
                           scan_frames=1,
                           scan_time=100000)
        self.init_plot()

    def init_device(self, device=''):
        #Initialize spectrometer device
        try:
            if (device =='#0'):
                #print('allo')
                #self.spec = sb.Spectrometer(sb.list_devices()[int(device[1:])])
                print('No spec serial number listed. Picking first spec found.')
                dev=list_devices()
                print dev
                self.spec = Spectrometer(dev[0])
            else:
                print('Serial number listed.')
                self.spec = Spectrometer.from_serial_number(device)
        except:
            print('ERROR: Could not initialize device "' + device + '"!')
            if (sb is None):
                print('SeaBreeze library not found!')
                sys.exit(1)
            else:
                print('Available devices:')
                index = 0
                for dev in list_devices():
                    print(' - #' + str(index) + ':', 'Model:', dev.model + '; serial number:', dev.serial)
                    index += 1
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
        self.timestamp = '%Y-%m-%dT%H:%M:%S%z'
        self.message = StringVar()
        self.total_exposure = int(scan_frames) * int(scan_time)
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

    def update_plot(self, scan_frames,enable_plot, i):
        if (self.measurement == scan_frames) or \
           (enable_plot > 0):
            self.graph.set_ydata(self.data)
            self.axes.relim()
            self.axes.autoscale_view(True, True, True)
    """
    def startplot(self):
        plot_animation= animation.FuncAnimation(self.figure, self.update_plot)
    """

    def start(self):
        self.T0 = time.time()
        #self.state = 'STBL'
        plot_animation= animation.FuncAnimation(self.figure, self.update_plot)
        TB.BasicThread.start(self) #Basicthread parent class start() runs the process()

    def process(self): #, scan_frames, autosave, autorepeat
            newData = list(map(lambda x,y:x-y, self.spec.intensities(), self.darkness_correction))
            if (self.measurement == 0):
                self.data = newData
            else:
                self.data = list(map(lambda x,y:x+y, self.data, newData))
            self.measurement += 1

            plot.suptitle(time.strftime(self.timestamp, time.gmtime()) +
                         ' (sum of ' + str(self.measurement) + ' measurement(s)' +
                         ' with integration time ' + str(self.scan_time.get()) + ' us)')

            if (self.measurement % 100 == 0):
                print("'O', end='', flush=True")
            elif (self.measurement % 10 == 0):
                print("'o', end='', flush=True")
            else:
                print("'.', end='', flush=True")
            if (self.scan_frames > 0):
                if self.measurement % self.scan_frames == 0:
                    #print(time.strftime(self.timestamp, time.gmtime()), self.data)
                    if self.autosave != 0:
                        self.save()
                    self.measurement = 0
                    if autorepeat == 0:
                        self.run_measurement = False
                        #self.button_startpause_text.set(self.button_startpause_texts[self.run_measurement])
                        #self.button_stopdarkness_text.set(self.button_stopdarkness_texts[self.run_measurement])
                        #self.message.set('Ready.')

        #self.root.after(1, self.measure) #after 1 msec, run self.measure!
        #thread with period = 1, run self.measure.

    """
    def addViewer('UDP',udpSendPid.Send):
        return
    """

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
Server.
Class collecting spectrum from Ocean Optics spectrometer in a thread.
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
from GSOF_ArduBridge import threadBasic as BT
from GSOF_ArduBridge import UDP_Send
import seabreeze
#seabreeze.use('pyseabreeze')
import seabreeze.spectrometers as sb
from seabreeze.spectrometers import Spectrometer, list_devices
'''
try:
    import seabreeze
    seabreeze.use('pyseabreeze')
    import seabreeze.spectrometers as sb
    from sb import Spectrometer, list_devices
except ImportError:
    sb=None
'''
# Plotting
import matplotlib.animation as animation
import matplotlib.pyplot as plot
plot_animation= None

class SBSimulator:
    """SeaBreeze specrogrameter simulator class"""
    def __init__(self,
                 integration_time_micros=100000,
                 minimum_integration_time_micros = 8000,
                 wavelengths=list(range(2048)),
                 generator=numpy.random.normal,
                 histogram=True):
        self._integration_time_micros = integration_time_micros
        self.minimum_integration_time_micros = minimum_integration_time_micros
        self._wavelengths = wavelengths
        self.samplesize = len(wavelengths)
        self.generator = generator
        self.histogram = histogram

    def integration_time_micros(self, newValue):
        if (newValue >= self.minimum_integration_time_micros):
            self._integration_time_micros = newValue

    def intensities(self):
        time.sleep(self._integration_time_micros / 1000000)
        if self.histogram:
            return(numpy.histogram(self.generator(size=self.samplesize), bins=self.samplesize)[0])
        else:
            return(self.generator(size=self.samplesize))

    def wavelengths(self):
        return(self._wavelengths)

class Flame(BT.BasicThread):
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
        BT.BasicThread.__init__(self, nameID=nameID, Period = Period, viewer=viewer)
        self.T0 = time.time()
        self.SPECstatus = False
        self.init_device(device=device)
        print("dev init")
        self.init_variables(
                           autoexposure=False,
                           autorepeat=True,
                           autosave=False,
                           dark_frames=1,
                           enable_plot=True,
                           output_file='Snapshot-%Y-%m-%dT%H:%M:%S%z.dat', #saved file name
                           scan_frames=1, #
                           scan_time=100000) #integration time
        print("var init")
        #self.init_plot()
        #print("plot init")

    def init_device(self, device=''):
        #Initialize spectrometer device
        try:
            #if (device =='#0'):
                #print('allo')
                #self.spec = sb.Spectrometer(sb.list_devices()[int(device[1:])])
            print('No spec serial number listed. Picking first spec found.')
            dev=list_devices()
            print dev
            self.spec = Spectrometer(dev[0])
            """
            else:
                print('Serial number listed.')
                self.spec = Spectrometer.from_serial_number(device)
            """
        except:
            print('ERROR: Could not initialize device "' + device + '"!')
            if (sb is None):
                print('SeaBreeze library not found!')
                #sys.exit(1)
            else:
                print('Available devices:')
                index = 0
                for dev in list_devices():
                    print(' - #' + str(index) + ':', 'Model:', dev.model + '; serial number:', dev.serial)
                    index += 1
            if ('Y'.startswith(input('Simulate spectrometer device instead?  [Y/n] ').upper())):
                self.spectrometer = SBSimulator()
            else:
                sys.exit(1)
        print(self.spec)
        self.wavelengths = self.spec.wavelengths()
        self.samplesize = len(self.wavelengths)

    def init_variables(self,
                       autoexposure=False,
                       autorepeat=False,
                       autosave=False,
                       dark_frames=1,
                       enable_plot=True,
                       output_file='Snapshot-%Y-%m-%dT%H:%M:%S%z.dat',
                       scan_frames=1,
                       scan_time=100000):
        """Initialize instance variables"""
        self.run_measurement = False
        self.have_darkness_correction = False
        self.autoexposure = autoexposure
        self.autorepeat = autorepeat
        self.autosave =autosave
        self.dark_frames = dark_frames
        self.enable_plot = enable_plot
        self.output_file = output_file
        self.scan_frames = scan_frames
        self.scan_time = scan_time
        self.timestamp = '%Y-%m-%dT%H:%M:%S%z'
        #self.message = StringVar()
        self.total_exposure = int(self.scan_frames) * int(self.scan_time)
        # Initialize variables
        self.darkness_correction = [0.0]*(len(self.spec.wavelengths()))
        self.measurement = 0
        self.data = [0.0]*(len(self.spec.wavelengths()))
        self.client=False

    def start(self):
        """Start the Threading process
        """
        self.SPECstatus = True
        self.T0 = time.time()
        try:
            self.viewer['TCPspec'].udpTx.listen(5) #stream 5 at a time
            print 'Listening for client...'
            while True:
                print 'Please run spec viewer.'
                self.client, addr = self.viewer['TCPspec'].udpTx.accept() #blocking call. While loop waits here until conn accepted.
                print 'Connected and starting thread...'
                BT.BasicThread.start(self)
        except:
            print 'Something went wrong. Can not connect to client.'

    def stop(self):
        """Stop the Threading process
        """
        self.SPECstatus = False
        BT.BasicThread.stop(self)

    def process(self):
        """This is invoked by run() of the Threading class. This process is repeated, with a Period.
        """
        #perform darkness Correction
        newData = list(map(lambda x,y: x-y, self.spec.intensities(), self.darkness_correction)) # intensities - darkness correction
        if (self.measurement == 0):
            self.data = newData
        else:
            self.data = list(map(lambda x,y: x+y, self.data, newData)) #newdata= sum of old data + new data
        d={'Msr':self.measurement,'L':self.wavelengths,'Dat':self.data}
        #sending data disctionary to client, by TCP
        self.send_df(d,self.client)
        print 'NewData sent to Client'
        self.measurement += 1
        if ((self.measurement % 100) == 0):
            print 'O', #py3: print ('O', end='', flush=True)
        elif (self.measurement % 10) == 0:
            print 'o', #py3: print('o', end='', flush=True)
        else:
            print '.',
            #py3: print('.', end='', flush=True)
        if (self.scan_frames > 0):
            if self.measurement % self.scan_frames == 0: # all frames are summed
                if self.autosave != 0:
                    #self.save()
                    print 'cant save'
                self.measurement = 0
                if self.autorepeat == 0:
                    self.run_measurement = False
                    #self.button_startpause_text.set(self.button_startpause_texts[self.run_measurement])
                    #self.button_stopdarkness_text.set(self.button_stopdarkness_texts[self.run_measurement])
                    #self.message.set('Ready.')

    def send_df(self,d,c):
        """Function to send data to TCP client
        """
        print 'sending...'
        self.viewer['TCPspec'].Send(d,c) #ardubridge defined specViewer, client

    def teleUpdate(self,tele):
            print str(tele)

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
Flame Class, uses Seabreeze to collect spectrum from Ocean Optics spectrometer.
Data collection is threaded.
TCP Server. Data is sent to TCP client, SpecPlot (tcpControl).
Based on and adapted from SpectrOMat, copyright Tobias Dusa. See:
"""


__version__ = "1.0.0"
__author__ = "Kenza Samlali"
__copyright__ = "Copyright 2019-2020"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = ""
__status__ = "Production"

import math, time
import sys
import numpy as np
import scipy.signal as sps
from GSOF_ArduBridge import threadBasic as BT
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
plot_animation = None

class SBSimulator:
    """SeaBreeze specrogrameter simulator class"""
    def __init__(self,
                 integration_time_micros=100000,
                 minimum_integration_time_micros = 8000,
                 wavelengths=list(range(2048)),
                 generator=np.random.normal,
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
            return(np.histogram(self.generator(size=self.samplesize), bins=self.samplesize)[0])
        else:
            return(self.generator(size=self.samplesize))

    def wavelengths(self):
        return(self._wavelengths)

class Flame(BT.BasicThread):
    def __init__(self,
                nameID,
                device,
                autorepeat,
                autosave,
                dark_frames,
                enable_plot,
                output_file,
                scan_frames,
                scan_time,
                viewer={}
                ):
        BT.BasicThread.__init__(self, nameID=nameID, Period=0, viewer=viewer)
        self.T0 = time.time()
        self.SPECstatus = False
        self.init_device(device = device)
        self.init_variables(
                           autorepeat = autorepeat,
                           autosave = autosave,
                           dark_frames = dark_frames,
                           enable_plot = enable_plot,
                           output_file = output_file,
                           scan_frames = scan_frames,
                           scan_time = scan_time)
        self.set_int_time(self.scan_time)
        #self.spec.integration_time_micros(self.scan_time)

    def init_device(self, device=''):
        #Initialize spectrometer device
        try:
            #if (device =='#0'):
                #print('allo')
                #self.spec = sb.Spectrometer(sb.list_devices()[int(device[1:])])
            print('No spec serial number listed. Picking first spec found.')
            dev = list_devices()
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
                self.spec = SBSimulator()
            else:
                sys.exit(1)
        print(self.spec)

    def init_variables(self,
                       autorepeat,
                       autosave,
                       dark_frames,
                       enable_plot,
                       output_file,
                       scan_frames,
                       scan_time
                       ):
        """Initialize instance variables"""
        self.autorepeat = autorepeat
        self.autosave = autosave
        self.dark_frames = dark_frames
        self.enable_plot = enable_plot
        self.output_file = output_file
        self.scan_frames = scan_frames
        self.scan_time = scan_time
        """Set remaining"""
        self.run_measurement = False
        self.enable = False
        self.have_darkness_correction = False
        self.timestamp = '%Y-%m-%dT%H:%M:%S%z'
        #self.total_exposure = int(self.scan_frames) * int(self.scan_time)
        # Initialize variables
        self.measurement = 0
        self.rawwavelengths = self.spec.wavelengths()
        self.wavelengths = self.rawwavelengths[2:]
        self.samplesize = len(self.wavelengths)
        self.darkness_correction = [0.0]*(len(self.rawwavelengths))
        self.data = [0.0]*(self.samplesize)
        self.client = None # TCP client, the Specplot.py
        self.SPS = None #Signal processing class instance set from Ardubridge

    def set_int_time(self,time): #integration time in microseconds
        self.spec.integration_time_micros(time)

    def start(self):
        """Start the Threading process
        BT.basicthread overwrite: add Server
        """
        self.SPECstatus = True
        #self.T0 = time.time()
        self.enable=True
        #self.run_measurement = True
        try:
            print('Listening for client...')
            self.viewer['TCPspec'].tcpTx.listen(5) #stream 5 at a time
            #while True:
            print('Please run spec viewer. Accepting connection ...')
            self.client, addr = self.viewer['TCPspec'].tcpTx.accept() #blocking call. While loop waits here until conn accepted.
            print('Connected and starting thread...')
            BT.BasicThread.start(self)
            print('%s: Started ON line'%(self.name))
            #play()
        except:
            print('Something went wrong. Can not connect to client.')

    def stop(self):
        """Stop the Threading process
        BT.basicthread overwrite:
        """
        self.SPECstatus = False
        #self.run_measurement = False
        self.enable = False
        BT.BasicThread.stop(self)

    def pause(self):
        #self.run_measurement = False
        if self.SPECstatus:
            self.enable = False
        else:
            print('Thread is not running in the first place!')

    def play(self):
        """restart the Threading process
        """
        if self.SPECstatus:
            #self.run_measurement = True
            self.enable=True
            BT.BasicThread.start(self)
            print('%s: Started ON line'%(self.name))
        else:
            print('You need to Spec.start() first!')

    def run(self):
        """
        The thread code that manages the periodic run, pause/play and stop.
        BT.basicthread overwrite: implement functionality with period = 0 
        """
        while (not(self.stopped())):
            self.lock.acquire(True)
            if self.enable:
                ## \/ Code begins below \/
                self.process()
                ## /\  Code ends above  /\

            ## *** Calculating how much time to wait until the next execution ***
            if self.Period > 0:
                self.T_Z[1] = self.T_Z[0]
                self.T_Z[0] += self.Period
                sleepTime = self.T_Z[0] - time.time()
                if sleepTime < 0.05:
                    while sleepTime < 0.05:
                        self.T_Z[0] += self.Period
                        sleepTime += self.Period
                    s = '%s: Timing error - Skipping a cycle'%(self.name)
                    #self.teleUpdate(s)
                    print(s)
                self.lock.release()
                time.sleep(sleepTime)
            else:
                self.lock.release()
        self.enable = False
        print('%s: Terminated\n'%(self.name))

    def draft_data(self):
        with open('Spectrometer Data/YData-20210208-T18h32m07s.dat' , 'r') as f:
            for line in f:
                num=line
                a = np.fromstring(num[1:-1], sep=',') #, dtype=np.float
        return a

    def process(self):
        """This is invoked by run() of the Threading class. This process is repeated, with a Period.
        BT.basicthread overwrite: Spectrometer data reading and sending to client.
        """
        #if self.run_measurement:
        """Read NewData and perform darkness Correction"""
        '''
        #couple of lines to test experimental data
        simul = False
        if simul == True:
            self.data = self.draft_data()
            d={'Msr':self.measurement, 'L':self.wavelengths, 'Dat':self.data}
        else:
        '''
        newData = list(map(lambda x,y: x-y, self.spec.intensities(), self.darkness_correction)) # intensities - darkness correction
        if (self.measurement == 0):
            self.data = newData[2:]
        else:
            sumdata = list(map(lambda x,y: x+y, self.data, newData)) #newdata= sum of old data + new data
            self.data = sumdata[2:]
        #d={'Msr':self.measurement, 'L':self.wavelengths, 'Dat':self.data, 'Peaks':peaks}
        d={'Msr':self.measurement, 'L':self.wavelengths, 'Dat':self.data}
        if self.SPS != None:
            #dndata = self.SPS.denoising(self.data)
            peak_int, peak_wvl = self.SPS.findallpeaks(self.wavelengths, self.data)
            dndata = self.data
            d = {'Msr':self.measurement, 'L':self.wavelengths, 'Dat':self.data, 'Peak_wvl':peak_wvl,'Peak_int':peak_int, 'Threshold':self.SPS.threshold , 'DatDn':dndata}
        """sending data dictionary to client, by TCP"""
        self.send_df(d, self.client)
        self.measurement += 1
        '''printouts during thread:
        if ((self.measurement % 100) == 0):
            print('O'), #py3: print ('O', end='', flush=True)
        elif (self.measurement % 10) == 0:
            print('o'), #py3: print('o', end='', flush=True)
        else:
            print('.'),
            #py3: print('.', end='', flush=True)
        '''
        if (self.scan_frames > 0):
            if self.measurement % self.scan_frames == 0: # all frames are summed
                if self.autosave != 0:
                    self.save()
                    print('Saving failed')
                self.measurement = 0
                if self.autorepeat == 0:
                    self.enable = False
                    #self.run_measurement = False
                    #self.button_startpause_text.set(self.button_startpause_texts[self.run_measurement])
                    #self.button_stopdarkness_text.set(self.button_stopdarkness_texts[self.run_measurement])
                    #self.message.set('Ready.')

    def background(self):
        if self.run_measurement:
            self.run_measurement = False
            #self.button_startpause_text.set(self.button_startpause_texts[self.run_measurement])
            #self.button_stopdarkness_text.set(self.button_stopdarkness_texts[self.run_measurement])
            #self.teleUpdate('Ready.')
            self.measurement = 0
        else:
            newData = self.spec.intensities()
            count = 1
            #self.message.set('Scanning dark frame ' + str(count) + '/' + str(self.dark_frames.get()))
            #self.root.update()
            #print('Scanning dark frame ' + str(count) + '/' + str(self.dark_frames))
            while count < int(self.dark_frames.get()):
                newData = list(map(lambda x,y:x+y, self.spec.intensities(), newData))
                '''printouts whhile thread is running:
                if (count % 100 == 0):
                    print('O'),
                elif (count % 10 == 0):
                    print('o'),
                else:
                    print('.'),
                '''
                count += 1
                #self.message.set('Scanning dark frame ' + str(count) + '/' + str(self.dark_frames.get()))
            self.darkness_correction = list(map(lambda x:x/count, newData))
            self.have_darkness_correction = True # important for saving file
            #self.axes.set_ylabel('Intensity [corrected count]')
            #print(str(self.dark_frames) + ' dark frames scanned. Ready.')

    def save(self):
        #try:
        #filename = 'Snapshot-%s.dat' %(time.strftime(self.timestamp, time.gmtime()))
        filename = time.strftime('Snapshot-%Y%m%d-T%Hh%Mm%Ss.dat', time.gmtime())
        with open(filename, 'w') as f: #time.strftime('Snapshot-%Y-%m-%dT%H:%M:%S.dat', time.gmtime())
            f.write('# FLAME spectrum data format')
            f.write('\n# Time of snapshot: ' + time.strftime(self.timestamp, time.gmtime()))
            f.write('\n# Number of frames accumulated: ' + str(self.measurement))
            f.write('\n# Scan time per exposure [us]: ' + str(self.scan_time))
            '''
            if self.have_darkness_correction:
                f.write('\n# Number of dark frames accumulated: ' + str(self.dark_frames.get()))
                f.write('\n# Wavelength [nm], dark frame correction data [averaged count]:\n# ')
                f.write('\n# '.join(map(lambda x,y:str(x)+', '+str(y), self.spec.wavelengths(), self.darkness_correction)))
                f.write('\n# Wavelength [nm], Intensity [corrected count]:\n')
            else:
                f.write('\n# Number of dark frames accumulated: None.')
                f.write('\n# Wavelength [nm], Intensity [count]:\n')
            f.write('\n'.join(map(lambda x,y:str(x)+', '+str(y), self.spec.wavelengths(), self.data)) + '\n')
            '''
            f.write('\n# Wavelength [nm], Intensity [count]:\n')
            f.write('\n'.join(map(lambda x,y:str(x)+', '+str(y), self.wavelengths, self.data)) + '\n')
            #f.write('\n# Dataframe sent over TCP: ' + d
        filename2 = time.strftime('YData-%Y%m%d-T%Hh%Mm%Ss.dat', time.gmtime())
        with open(filename2, 'w') as f: #time.strftime('Snapshot-%Y-%m-%dT%H:%M:%S.dat', time.gmtime())
            f.write(str(self.data))
        print('Data saved to ' + filename)
        #except:
        #    print('Error while writing ' + time.strftime('Snapshot-%Y-%m-%dT%H:%M:%S.dat', time.gmtime()))

    def send_df(self,d,c):
        """Function to send data to TCP client
        """
        #print 'sending...'
        self.viewer['TCPspec'].Send(d,c) #ardubridge defined specViewer, client


class Processing(BT.BasicThread):
    def __init__(self,
                 gpio,
                 Period,
                 nameID,
                 threshold,
                 noise,
                 DenoiseType,
                 PeakProminence,
                 PeakThreshold,
                 PeakWidth,
                 PeakWlen,
                 Peak_range,
                 Pin_cte,
                 Pin_pulse,
                 Pin_onTime,
                 t_wait,
                 ):
        BT.BasicThread.__init__(self, nameID=nameID, Period=Period, viewer={})
        self.gpio = gpio
        self.T0 = time.time()
        self.threshold = threshold
        self.peaks= False #np.array([])
        self.denoise = False
        self.noise = noise
        self.prom = PeakProminence
        self.width = PeakWidth
        self.wlen = PeakWlen
        self.dist = PeakThreshold
        self.type = DenoiseType
        self.range = Peak_range
        self.pin_ct = Pin_cte
        self.pin_pulse = Pin_pulse
        self.onTime = Pin_onTime
        self.run_autosort = False
        # Instances set by ardubridge
        self.enOut = False
        self.spec= None 
        #set for test
        self.t_wait=t_wait

    def draft_data(self):
        ''' Use this function to test specSP functions on saved data (Spec.save())
        '''
        with open('Spectrometer data/YData-20210208-T18h32m07s.dat' , 'r') as f:
            for line in f:
                num=line
                a = np.fromstring(num[1:-1], sep=',') #, dtype=np.float
        return a

    def denoising(self, y):
        '''y = Intensity list
        Function to denoise y-data.
        BW, Buterworth filter
        SG, Savitzky-Golay filter
        '''
        self.denoise = True
        if self.type == 'BW':
            N  = 3 # Filter polynomial order
            Wn = 0.1 # Cutoff frequency
            B, A = sps.butter(N, Wn, output='ba')
            yf = sps.filtfilt(B, A, y)
        if self.type == 'SG':
            W = 5 # wl window size
            P = 3 # Flter polynomial order
            yf = sps.savgol_filter(y, 51, 3)
        else:
            print('Type needs to be BW or SG')
        return yf

    def findallpeaks(self, x, y):
        '''x = wavelength list, y = Intensity list
        Function to find peaks using scipy signal processing library
        '''
        self.peaks = True
        arr = np.asarray(y)
        peaks, properties = sps.find_peaks(arr,
                                         height = self.noise,
                                         threshold = self.dist,
                                         prominence = self.prom,
                                         width = self.width,
                                         wlen = self.wlen)
        #peak_ht = properties['peak_heights']
        peak_int = arr[peaks] #peaks is an index
        peak_wvl = x[peaks]
        return peak_int, peak_wvl

    def findpeaks(self, x, y):
        '''x = wavelength list, y = Intensity list
        Function to find all peaks above treshold using scipy
         signal processing library
        '''
        self.peaks = True
        int = np.asarray(y)
        peaks, properties = sps.find_peaks(int,
                                         height = self.threshold,
                                         threshold = self.dist,
                                         prominence = self.prom,
                                         width = self.width,
                                         wlen = self.wlen)
        #peak_ht = properties['peak_heights']
        peak_int = int[peaks] 
        peak_wvl = x[peaks]
        return peak_int, peak_wvl

    def enIO(self, val):
        ''' Function used in ArduBridge, to turn comm on 
        '''
        self.enOut = True
    
    def start(self):
        ''' Start the thread for peak detection and actuating 
        electrode pattern for sorting, after 'wait' seconds 
        '''
        print('Starting thread...')
        self.run_autosort = True
        BT.BasicThread.start(self)
        #turn bottomn elec on
        print('%s: Started ON line'%(self.name))
        if self.enOut:
                self.gpio.pinWrite(self.pin_ct, 1)
                self.teleUpdate('%s, E%d: 1'%(self.name, self.pin_ct))
    
    def process(self):
        peakfound = False
        try:
            p_int, p_wvl = self.findpeaks(self.spec.wavelengths, self.spec.data)
            #p_int, p_wvl = self.findpeaks(self.spec.wavelengths, self.draft_data())
            print p_int
            print p_wvl
            z = [i for i in p_wvl if (self.range[0]< i <self.range[1])]
            if len(z) > 0: zz = True
            if len(p_int) > 0:
                #if peakrange = True:
                if (self.range == None) or zz:
                    peakfound=True
                    #wait, depending on distance between detection and electrodes
                    time.sleep(self.t_wait)
                    #turn top elec on
                    if self.enOut:
                        self.gpio.pinPulse(self.pin_pulse, self.onTime)
                        self.teleUpdate('%s, E%d: %f s pulse'%(self.name, self.pin_pulse, self.onTime))
        except:
            print('Error...')
            exc_type, exc_value = sys.exc_info()[:2]
            print '%s : Handling %s exception with message "%s"' % \
                (self.name, exc_type.__name__, exc_value)
            #stop thread???

    def stop(self):
        '''Function stopping the thread and turning elecs off
        '''
        self.run_autosort = False
        self.enable = False
        self.gpio.pinWrite(self.pin_ct, 0)
        self.teleUpdate('%s, E%d: 0'%(self.name, self.pin_ct))
        self.enOut = False
        print('Stopping thread...')
        BT.BasicThread.stop(self)
        
    
    def pause(self):
        """pause the Threading process
        """
        self.run_autosort = False
        self.enable = False

    def play(self):
        """restart the Threading process
        """
        self.run_autosort = True
        self.enable = True
        BT.BasicThread.start(self)
        print('%s: Started ON line'%(self.name))   
    
            


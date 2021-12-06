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
from datetime import timedelta, datetime
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

    def init_device(self, device=''):
        #Initialize spectrometer device
        try:
            print('No spec serial number listed. Picking first spec found.')
            dev = list_devices()
            print(dev)
            self.spec = Spectrometer(dev[0])
            """
            else:
                print('Serial number listed.')
                self.spec = Spectrometer.from_serial_number(device)
            """
        except:
            print(('ERROR: Could not initialize device "' + device + '"!'))
            if (sb is None):
                print('SeaBreeze library not found!')
                #sys.exit(1)
            else:
                print('Available devices:')
                index = 0
                for dev in list_devices():
                    print((' - #' + str(index) + ':', 'Model:', dev.model + '; serial number:', dev.serial))
                    index += 1
<<<<<<< HEAD:fungalmicrofluidics/build/threadSpec.py
            if input('Simulate spectrometer device instead?  [Y/n] ') == 'Y': #.upper()
=======
            if raw_input('Simulate spectrometer device instead?  [Y/n] ') == 'Y': #.upper()
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/threadSpec.py
                self.spec = SBSimulator()
            else:
                sys.exit(1)
        print((self.spec))

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
        # Initialize variables
        self.measurement = 0
        self.rawwavelengths = self.spec.wavelengths()
        self.wavelengths = self.rawwavelengths[2:]
        self.samplesize = len(self.wavelengths)
        self.darkness_correction = [0.0]*(len(self.rawwavelengths))
        self.data = [0.0]*(self.samplesize)
        self.client = None # TCP client, the Specplot.py
        self.SPS = None #Signal processing class instance set from Ardubridge

    def set_int_time(self,t):
        '''Set the integration time of the FLAME spectrometer.
        t = time in msec'''
        try:
            self.spec.integration_time_micros(t)
<<<<<<< HEAD:fungalmicrofluidics/build/threadSpec.py
            print("Integration time set to {} ms".format(t))
=======
            print ("Integration time set to %d ms") %(t)
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/threadSpec.py
        except:
            print("Error. Can't set integrtion time.")
        
    def start(self):
        """Start the Threading process
        BT.basicthread overwrite: add Server
        """
        self.SPECstatus = True
        self.enable=True
        try:
            print('Listening for client...')
            self.viewer['TCPspec'].tcpTx.listen(5) #stream 5 at a time
            print('Please run spec viewer. Accepting connection ...')
            self.client, addr = self.viewer['TCPspec'].tcpTx.accept() #blocking call. While loop waits here until conn accepted.
            print('Connected and starting thread...')
            BT.BasicThread.start(self)
            print('{}: Started ON line'.format(self.name))
        except:
            print('Something went wrong. Can not connect to client.')

    def stop(self):
        """Stop the Threading process
        BT.basicthread overwrite:
        """
        self.SPECstatus = False
        self.enable = False
        BT.BasicThread.stop(self)

    def pause(self):
        if self.SPECstatus:
            self.enable = False
        else:
            print('Thread is not running in the first place!')

    def play(self):
        """restart the Threading process
        """
        if self.SPECstatus:
            self.enable=True
            BT.BasicThread.start(self)
            print('{}: Started ON line'.format(self.name))
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
                    s = '{}: Timing error - Skipping a cycle'%(self.name)
                    print(s)
                self.lock.release()
                time.sleep(sleepTime)
            else:
                self.lock.release()
        self.enable = False
        print(('{}: Terminated\n'%(self.name)))

    @staticmethod
    def draft_data():
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
        newData = [(i > 0) * i for i in newData] #remove all negative values
        if (self.measurement == 0):
            self.data = newData[2:] #remove 2 first data points
        else:
            sumdata = list(map(lambda x,y: x+y, self.data, newData)) #newdata= sum of old data + new data
            self.data = sumdata[2:] #remove 2 first data points
        
        if self.SPS != None: # Processing is ON
            try:
                dndata = self.SPS.denoising(self.data) # denoised data
                peak_int, peak_wvl = self.SPS.findallpeaks(self.wavelengths, self.data) # Peak data
                full_gate = self.SPS.gateI + self.SPS.gateL # Gate data
                d = {'Msr':self.measurement, 'L':self.wavelengths, 'Dat':self.data, 'Peak_wvl':peak_wvl,'Peak_int':peak_int, 'Gate':full_gate , 'DatDn':dndata}
            except:
                print('Exception. Something wrong with Signal Processing.')
        else: # Processing is OFF
            d={'Msr':self.measurement, 'L':self.wavelengths, 'Dat':self.data}
        """sending data dictionary to client, by TCP"""
        self.send_df(d, self.client)
        self.measurement += 1
        if (self.scan_frames > 0):
            if self.measurement % self.scan_frames == 0: # all frames are summed
                if self.autosave != 0:
                    self.save()
                    print('Saving failed')
                self.measurement = 0
                if self.autorepeat == 0:
                    self.enable = False

    def background(self):
        """ Apply background substraction.
        """
        if self.enable: #self.run_measurement: # if currently running a measurement
            self.pause()
            self.measurement = 0
        print('Paused. Acquiring data for dark frames...')
        newData = self.spec.intensities()
        count = 1
        print(('Scanning dark frame ' + str(count) + '/' + str(self.dark_frames)))
        while count < int(self.dark_frames):
            newData = list(map(lambda x,y:x+y, self.spec.intensities(), newData))
            '''printouts while thread is running:
            if (count % 100 == 0):
                print('O'),
            elif (count % 10 == 0):
                print('o'),
            else:
                print('.'),
            '''
            count += 1
        self.darkness_correction = list([x/count for x in newData])
        self.have_darkness_correction = True # important for saving file
        print((str(self.dark_frames) + ' dark frames scanned. Ready. Press Play (or >>> Spec.play() ). Spec.reset() to remove background substraction.'))

    def reset(self):
        """Clear background substraction and reset all applied values.""" #New instance of Processing??
        self.enable = False
        self.darkness_correction = [0.0]*(len(self.rawwavelengths))
        self.have_darkness_correction = False
        print('Reset. Press Play to restart (or >>>Spec.play())')
        

    def save(self):
        filename = time.strftime('Snapshot-%Y%m%d-T%Hh%Mm%Ss.dat', time.gmtime())
        loc='Spectrometer Data/'
        file = loc+filename
        with open(file, 'w') as f: #time.strftime('Snapshot-%Y-%m-%dT%H:%M:%S.dat', time.gmtime())
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
        filename2 = time.strftime('YData-%Y%m%d-T%Hh%Mm%Ss.dat', time.gmtime())
        file2 = loc+filename2
        with open(filename2, 'w') as f: #time.strftime('Snapshot-%Y-%m-%dT%H:%M:%S.dat', time.gmtime())
            f.write(str(self.data))
<<<<<<< HEAD:fungalmicrofluidics/build/threadSpec.py
        print(('Data saved to ' + file2 + ', YData saved to ' + file2))
        
=======
        print('Data saved to ' + file2 + ', YData saved to ' + file2)
        #except:
        #    print('Error while writing ' + time.strftime('Snapshot-%Y-%m-%dT%H:%M:%S.dat', time.gmtime()))

>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/threadSpec.py
    def send_df(self,d,c):
        """ Function to send data to TCP client
        """
        #print 'sending...'
        self.viewer['TCPspec'].Send(d,c) #ardubridge defined specViewer, client


class Processing(BT.BasicThread):
    def __init__(self,
                 gpio,
                 Period,
                 nameID,
                 intensity_gate,
                 wavelength_gate,
                 pkcount,
                 noise,
                 DenoiseType,
                 PeakProminence,
                 PeakThreshold,
                 PeakWidth,
                 PeakWlen,
                 AutoSave,
                 output_file,
                 Elec,
                 Pin_cte,
                 Pin_pulse,
                 Pin_onTime,
                 t_wait
                 ):
        BT.BasicThread.__init__(self, nameID=nameID, Period=Period, viewer={})
        self.gpio = gpio
        self.gateI = intensity_gate
        self.gateL = wavelength_gate
        self.peakcnt = pkcount
        self.SAVE = AutoSave
        self.output_file = output_file
        self.denoise = False
        self.noise = noise
        self.prom = PeakProminence
        self.width = PeakWidth
        self.wlen = PeakWlen
        self.dist = PeakThreshold
        self.type = DenoiseType
        self.electhread = Elec
        self.pin_ct = Pin_cte
        self.pin_pulse = Pin_pulse
        self.onTime = Pin_onTime
        self.t_wait=t_wait
        
        # Instances set by ardubridge
        self.enOut = False
        self.spec= None 
        #Other
        self.T0 = time.time()
        self.peaks= False #np.array([])
        self.autosort_status = False
        self.cntr = 0
        
    @staticmethod
    def countevents(cnt):
        if cnt == 0 or cnt == False:
            COUNT = False
        else:
            COUNT = True
        return COUNT

    @staticmethod
    def draft_data():
        ''' Use this function to test specSP functions on saved data (Spec.save())
        '''
        with open('Spectrometer Data/YData-20210208-T18h32m07s.dat' , 'r') as f:
            for line in f:
                num=line
                a = np.fromstring(num[1:-1], sep=',') #, dtype=np.float
        return a

    def denoising(self, y):
        """y = Intensity list
        Function to denoise y-data.
        BW, Buterworth filter
        SG, Savitzky-Golay filter
        See SciPy signal processing library
        """
        self.denoise = True
        try:
            if self.type == 'BW':
                N  = 3 # Filter polynomial order
                Wn = 0.1 # Cutoff frequency
                B, A = sps.butter(N, Wn, output='ba')
                yf = sps.filtfilt(B, A, y)
            elif self.type == 'SG':
                W = 5 # wl window size
                P = 3 # Flter polynomial order
                yf = sps.savgol_filter(y, 51, 3)
            return yf
        except:
            print('Type needs to be BW or SG. Can not perform denoising')
            raise

    def findallpeaks(self, x, y):
        """x = wavelength list, y = Intensity list
        Function to find peaks using scipy signal processing library
        """
        self.peaks = True
        arr = np.asarray(y)
        peaks, properties = sps.find_peaks(arr,
                                         height = self.noise,
                                         threshold = self.dist,
                                         prominence = self.prom,
                                         width = self.width,
                                         wlen = self.wlen)
        peak_int = arr[peaks] #peaks is an index
        peak_wvl = x[peaks]
        return peak_int, peak_wvl

    def findpeaks(self, x, y):
        """x = wavelength list, y = Intensity list
        Function to find all peaks above treshold using scipy
        signal processing library
        """
        self.peaks = True
        int = np.asarray(y)
        peaks, properties = sps.find_peaks(int,
                                         height = self.gateI,
                                         threshold = self.dist,
                                         prominence = self.prom,
                                         width = self.width,
                                         wlen = self.wlen)
        peak_int = int[peaks] 
        peak_wvl = x[peaks]
        return peak_int, peak_wvl

    def enIO(self,val):
        """Function used in ArduBridge, to turn comm on 
        """
        self.enOut = True
    
    def start(self):
        """Start the thread for peak detection and actuating 
        electrode pattern for sorting, after 'wait' seconds 
        """
        print('Starting thread...')
        self.autosort_status = True
        global start_time
        start_time = datetime.now()
        #Make file for saving data
        if self.SAVE:
            #global filename
            filename = time.strftime('PeakData-%Y%m%d-T%Hh%Mm%Ss.dat', time.gmtime())
            #global loc
            loc='Spectrometer Data/'
            global filepk
            filepk = loc+str(filename)
            with open(filepk, 'w') as f:
                f.write('\n# Time of snapshot: ' + time.strftime(self.spec.timestamp, time.gmtime()))
                f.write('\n# Number of frames accumulated: ' + str(self.spec.measurement))
                f.write('\n# Scan time per exposure [us]: ' + str(self.spec.scan_time))
                f.write('\n Wavelength [nm], Intensity [RFU]\n')
<<<<<<< HEAD:fungalmicrofluidics/build/threadSpec.py
            print(('Saving all data under ' +filepk))
=======
            print ('Saving all data under ' +filepk)
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/threadSpec.py
        #turn bottom electrode on
        if self.electhread and self.enOut:
            print('{}: Started ON line'.format(self.name))
            self.gpio.pinWrite(self.pin_ct, 1)
            self.teleUpdate('{}, E{}: 1'.format(self.name, self.pin_ct))
        # starting thread
        BT.BasicThread.start(self)
        
    
    def run(self):
        """
        The thread code that manages the periodic run, pause/play and stop.
        BT.basicthread overwrite: 
        - implement functionality with period = 0 
        - IMPLEMENT COUNT
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
<<<<<<< HEAD:fungalmicrofluidics/build/threadSpec.py
                    s = '{}: Timing error - Skipping a cycle'.format(self.name)
=======
                    s = '%s: Timing error - Skipping a cycle'%(self.name)
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/threadSpec.py
                    #self.teleUpdate(s)
                    print(s)
                self.lock.release()
                time.sleep(sleepTime)
            else:
                self.lock.release()
        self.enable = False
<<<<<<< HEAD:fungalmicrofluidics/build/threadSpec.py
        print('{}: Terminated\n'.format(self.name))
=======
        print('%s: Terminated\n'%(self.name))
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/threadSpec.py

    def process(self):
        peakfound = False
        #global pkcount
        try:
<<<<<<< HEAD:fungalmicrofluidics/build/threadSpec.py
            #Find all peaks above noise
            p_int, p_wvl = self.findallpeaks(self.spec.wavelengths, self.spec.data)
            #Filter out peaks outside gate
            wvl_list = [i for i in p_wvl if (self.gateL[0]< i <self.gateL[1])]
            int_list = [i for i in p_int if (self.gateI[0]< i <self.gateI[1])]
            zz = False
            if len(wvl_list) > 0: 
                zz = True
                print('Peak at:'+str(wvl_list))
            if len(p_int) > 0 and ( (self.gateL == None) or zz):
                if self.SAVE: 
                    self.savepeaks(filepk, p_wvl, p_int) #saves all peaks, including outside gate
                if len(wvl_list)>0 and len(int_list)>0:
                    peakfound = True
                    print('+++')
                    print(str(wvl_list)+'nm, '+str(int_list)+'A.U')
                    if self.countevents(self.peakcnt): 
                        if self.cntr == self.peakcnt:
                            self.lock.release()
                            self.enable = False
                            print('Final event.')
                            end_time = datetime.now()
                            self.stop()
                        self.cntr += 1
                        print('Peak '+str(self.cntr))
                    if self.electhread and self.enOut:
                        #wait, depending on distance between detection and electrodes
                        time.sleep(self.t_wait)
                        #turn top elec on
                        self.gpio.pinPulse(self.pin_pulse, self.onTime)
                        self.teleUpdate('{}, E%d: %f s pulse'%(self.name, self.pin_pulse, self.onTime))
=======
            #Find peaks within intesnity gate
            #p_int, p_wvl = self.findpeaks(self.spec.wavelengths, self.spec.data)
            #Find all peaks above noise
            p_int, p_wvl = self.findallpeaks(self.spec.wavelengths, self.spec.data)
            #print p_wvl,p_int
            #Filter out peaks outside x range
            z = [i for i in p_wvl if (self.gateL[0]< i <self.gateL[1])]
            zz = False
            if len(z) > 0: 
                zz = True
                print('Peak at:'+str(z)) 
            #if len(z) > 1: 
            #    '''Take this conditional statement and resp. exception away to sort even with 
            #    multiple peaks.'''
            #    raise ValueError('WARNING Multiple peaks within gate detected. Correct gate to sort.')
            if len(p_int) > 0 and ( (self.gateL == None) or zz):
                peakfound = True
                print('+++')
                if self.countevents(self.peakcnt): 
                    if self.cntr == self.peakcnt:
                        self.lock.release()
                        self.enable = False
                        print('Final event.')
                        end_time = datetime.now()
                        #print('Time elapsed:', end_time - start_time)
                        self.stop()
                    self.cntr += 1
                    print('Peak '+str(self.cntr))
                #print(str(p_wvl)+'nm, '+str(p_int)+'A.U')
                if self.SAVE: 
                    self.savepeaks(filepk, p_wvl, p_int) #saves all peaks, including outside gate
                if self.electhread and self.enOut:
                    #wait, depending on distance between detection and electrodes
                    time.sleep(self.t_wait)
                    #turn top elec on
                    self.gpio.pinPulse(self.pin_pulse, self.onTime)
                    self.teleUpdate('%s, E%d: %f s pulse'%(self.name, self.pin_pulse, self.onTime))

>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/threadSpec.py
        except ValueError as e:
            print(e)
        except:
            print('Error...')
            exc_type, exc_value = sys.exc_info()[:2]
<<<<<<< HEAD:fungalmicrofluidics/build/threadSpec.py
            print('{} : Handling {} exception with message "{}"'.format(self.name, exc_type.__name__, exc_value))
=======
            print '%s : Handling %s exception with message "%s"' % \
                (self.name, exc_type.__name__, exc_value)
            #stop thread???
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/threadSpec.py
    def stop(self):
        """Function stopping the thread and turning elecs off
        """
        self.autosort_status = False
        self.cntr = 0 # reset counter
        self.enable = False
        print('Stopping thread...')
        BT.BasicThread.stop(self)
        self.gpio.pinWrite(self.pin_ct, 0)
        self.gpio.pinWrite(self.pin_pulse, 0)
<<<<<<< HEAD:fungalmicrofluidics/build/threadSpec.py
        self.teleUpdate('{}, E{}: 0'.format(self.name, self.pin_ct))
=======
        self.teleUpdate('%s, E%d: 0'%(self.name, self.pin_ct))
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/threadSpec.py
        self.enOut = False
    
    def pause(self):
        """Pause the Threading process
        """
        self.autosort_status = False
        self.enable = False
<<<<<<< HEAD:fungalmicrofluidics/build/threadSpec.py
        self.gpio.pinWrite(self.pin_pulse, 0)
        self.teleUpdate('{}, E{}: 0'.format(self.name, self.pin_pulse))
=======
        #self.gpio.pinWrite(self.pin_ct, 0)
        self.gpio.pinWrite(self.pin_pulse, 0)
        self.teleUpdate('%s, E%d: 0'%(self.name, self.pin_pulse))
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/threadSpec.py

    def play(self):
        """Restart the Threading process
        """
        self.autosort_status = True
        self.enable=True
        BT.BasicThread.start(self)
        print(('{}: Started ON line'%(self.name)))   

    @staticmethod
    def savepeaks(name, xdata, ydata):
        """Append all detected peaks (wavelength, RFU) into one snapshot file.
        """
        fname = name
        with open(fname, 'a') as f:
            f.write('\n'.join(map(lambda x,y:str(x)+', '+str(y), xdata, ydata)) + '\n')
        print('Peak data added to ' + fname)

<<<<<<< HEAD:fungalmicrofluidics/build/threadSpec.py
    ''' Following are functions to set values from GUI
    '''
=======
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/threadSpec.py
    def setGate(self, lowerI, upperI, lowerL, upperL):
        '''set lower intensity, upper intensity, 
        lower wavelength, upper wavelength'''
        try:
            self.gateI = [lowerI, upperI]
<<<<<<< HEAD:fungalmicrofluidics/build/threadSpec.py
            print(("Gate set to %d - %d [RFU] ") %(lowerI, upperI))
            self.gateL = [lowerL,upperL]
            print(("Gate set to %d - %d [nm] ") %(lowerL, upperL))
=======
            print ("Gate set to %d - %d [RFU] ") %(lowerI, upperI)
            self.gateL = [lowerL,upperL]
            print ("Gate set to %d - %d [nm] ") %(lowerL, upperL)
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/threadSpec.py
        except:
            print("Error. Can't set gate.")

    def setDropTime(self,t):
        '''Set the droplet travel time (how long it takes for a droplet to travel from
         excitation point to sorting electrodes)
         t = time in sec'''
        try:
            self.t_wait = t
            print("Droplet travel time set to:" + str(t) )
        except:
            print("Error. Can't set Droplet travel Time.")

    def setOnTime(self, t):
        '''Set the onTime for the pulsing electrode.
        t = time in sec.
        '''
        try:
            self.onTime = t
<<<<<<< HEAD:fungalmicrofluidics/build/threadSpec.py
            print("onTime set to: {} sec ".format(str(t)))
=======
            print("onTime set to: %d sec "+ str(t) )
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/threadSpec.py
        except:
            print("Error. Can't set onTime.")

    def setElecs(self, pin_ct, pin_pulse):
        '''Set the electrode numbers for your sorting configuration.
        Set pin_ct = constant pin
        pin_pulse = pulsing sorting pin
        '''
        try:
            self.pin_ct = pin_ct
            self.pin_pulse = pin_pulse
<<<<<<< HEAD:fungalmicrofluidics/build/threadSpec.py
            print("Pin_cte: {} , Pin_pulse: {}.".format(pin_ct, pin_pulse))
=======
            print("Pin_cte: %d , Pin_pulse: %d.") %(pin_ct, pin_pulse)
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/threadSpec.py
        except:
            print("Error. Can't set pint_cte or pin_pulse.")

    def setEvents(self, nr):
        ''' Set nr of events to record
        '''
        try:
            self.pkcount = nr
            print("Events to be recorded: "+nr)
        except:
            print("Error. Can't set events nr.")

    def setAutoSave(self, bool):
        ''' Set peak saving on or off
        '''
        try:
            self.SAVE = bool
            print("Auto-save Peaks ON ")
        except:
<<<<<<< HEAD:fungalmicrofluidics/build/threadSpec.py
            print("Error. Can't set Auto-Save.")
=======
            print("Error. Can't set Auto-Save.")
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/threadSpec.py

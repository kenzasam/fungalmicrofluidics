from __future__ import print_function
import sys
if sys.version_info[:2] < (3, 3):
    old_print = print
    def print(*args, **kwargs):
        flush = kwargs.pop('flush', False)
        old_print(*args, **kwargs)
        if flush:
            file = kwargs.get('file', sys.stdout)
            # Why might file=None? IDK, but it works for print(i, file=None)
            file.flush() if file is not None else sys.stdout.flush()
########################

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
"""
"""
TO DO: Tk root
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
#import threadBasic as BT
from GSOF_ArduBridge import threadBasic as BT
#from GSOF_ArduBridge import PidAlgorithm
#from GSOF_ArduBridge import movAvg
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

try:
    # for Python2
    from Tkinter import *   ## notice capitalized T in Tkinter
    input = raw_input
except ImportError:
    # for Python3
    from tkinter import *   ## notice here too
# Plotting
import matplotlib.animation as animation
import matplotlib.pyplot as plot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
SpectrOMat_animation = None

class ArduFlameThread(BT.BasicThread):
    """
    """
    def __init__(self,
                bridge,
                nameID,
                Period,
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
                viewer={}
                 ):

        BT.BasicThread.__init__(self, nameID=nameID, Period=Period, viewer=viewer)
        self.ardu = bridge   #The Arduino-Bridge object
        #self.spectrometer = Spectrometer.from_serial_number(device)
        #self.spec = Spectrometer.from_first_available()
        print(device)
        self.init_device(device=device)
        self.init_tk(root=root)
        self.init_variables(
                            autoexposure=autoexposure,
                            autorepeat=autorepeat,
                            autosave=autosave,
                            dark_frames=dark_frames,
                            enable_plot=enable_plot,
                            output_file=output_file,
                            scan_frames=scan_frames,
                            scan_time=scan_time,
                            )
        self.init_plot()
        self.init_ui()

    def init_device(self, device='#0'):
        #Initialize spectrometer device
        try:
            if (device == ''):
            #    print('allo')
            #    self.spec = sb.Spectrometer(sb.list_devices()[int(device[1:])])
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
                    print('oi')
                    print(' - #' + str(index) + ':', 'Model:', dev.model + '; serial number:', dev.serial)
                    index += 1
                sys.exit(1)
        print(self.spec)
        self.wavelengths = self.spec.wavelengths()
        self.samplesize = len(self.wavelengths)
    def init_tk(self, root=None):
        """Initialize TK subsystem"""
        if root is None:
            root = Tk()
        self.root = root
        self.root.title('SpectrometerBridge')
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
        self.T0 = time.time() #wehre should this go????
        self.run_measurement = False
        self.have_darkness_correction = False
        self.button_startpause_texts = { True: 'Pause Measurement', False: 'Start Measurement' }
        self.button_stopdarkness_texts = { True: 'Stop Measurement', False: 'Get Darkness Correction' }
        self.autoexposure = IntVar(value=autoexposure)
        self.autorepeat = IntVar(value=autorepeat)
        self.autosave = IntVar(value=autosave)
        self.dark_frames = StringVar(value=dark_frames)
        self.enable_plot = IntVar(value=enable_plot)
        self.output_file = StringVar(value=output_file)
        self.scan_frames = StringVar(value=scan_frames)
        self.scan_time = StringVar(value=scan_time)
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
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)

    def init_ui(self):
        """Start the UI"""
	# Define the elements
        self.label_scan_frames = Label(self.root, text='Scan Frame Count', justify=LEFT)
        self.scale_scan_frames = Scale(self.root, from_=0, to=10000, showvalue=0, orient=HORIZONTAL, command=self.update_scan_frames)
        self.entry_scan_frames = Entry(self.root, textvariable=self.scan_frames, validate='focusout')

        self.label_scan_time = Label(self.root, text='Scan Time [us]', justify=LEFT)
        self.scale_scan_time = Scale(self.root, from_=self.spec.minimum_integration_time_micros, to=10000000, showvalue=0, orient=HORIZONTAL, command=self.update_scan_time)
        self.entry_scan_time = Entry(self.root, textvariable=self.scan_time, validate='focusout')

        self.label_dark_frames = Label(self.root, text='Dark Frame Count', justify=LEFT)
        self.scale_dark_frames = Scale(self.root, from_=1, to=10000, showvalue=0, orient=HORIZONTAL, command=self.update_dark_frames)
        self.entry_dark_frames = Entry(self.root, textvariable=self.dark_frames, validate='focusout')

        self.entry_scan_frames.config({'validatecommand': self.validate_scan_frames})
        self.entry_scan_time.config({'validatecommand': self.validate_scan_time})
        self.entry_dark_frames.config({'validatecommand': self.validate_dark_frames})

        self.button_startpause_text = StringVar()
        self.button_startpause_text.set(self.button_startpause_texts[self.run_measurement])
        self.button_startpause = Button(self.root, textvariable=self.button_startpause_text, command=self.startpause)

        self.checkbutton_enable_plot = Checkbutton(self.root, text='Enable Live Plotting', variable=self.enable_plot)

        self.checkbutton_autorepeat = Checkbutton(self.root, text='Auto Repeat', variable=self.autorepeat)
        self.checkbutton_autosave = Checkbutton(self.root, text='Auto Save', variable=self.autosave)
        self.checkbutton_autoexposure = Checkbutton(self.root, text='Constant Total Exposure', variable=self.autoexposure)

        self.button_stopdarkness_text = StringVar()
        self.button_stopdarkness_text.set(self.button_stopdarkness_texts[self.run_measurement])
        self.button_stopdarkness = Button(self.root, textvariable=self.button_stopdarkness_text, command=self.stopdarkness)

        self.button_save = Button(self.root, text='Save to File', command=self.save)
        self.button_reset = Button(self.root, text='Reset', command=self.reset)
        self.button_exit = Button(self.root, text='Exit', command=self.exit)

        self.textbox = Label(self.root, fg='white', bg='black', textvariable=self.message)
        self.message.set('Ready.')

        # Define the layout
        self.label_scan_frames.grid(rowspan=2)
        self.scale_scan_frames.grid(row=0, column=1, rowspan=2)
        self.entry_scan_frames.grid(row=1, column=2)

        self.label_scan_time.grid(rowspan=2)
        self.scale_scan_time.grid(row=2, column=1, rowspan=2)
        self.entry_scan_time.grid(row=3, column=2)

        self.label_dark_frames.grid(rowspan=2)
        self.scale_dark_frames.grid(row=4, column=1, rowspan=2)
        self.entry_dark_frames.grid(row=5, column=2)

        self.checkbutton_autorepeat.grid(row=6)
        self.checkbutton_autosave.grid(row=6, column=1)
        self.checkbutton_autoexposure.grid(row=6, column=2)

        self.button_startpause.grid(row=7)
        self.checkbutton_enable_plot.grid(row=7, column=1)
        self.button_stopdarkness.grid(row=7, column=2)

        self.button_save.grid(row=8)
        self.button_reset.grid(row=8, column=1)
        self.button_exit.grid(row=8, column=2)

        self.textbox.grid(columnspan=3)

        self.canvas.get_tk_widget().grid(columnspan=3)

	# Start the infinite measurement loop
        self.root.after(1, self.measure)

    #@staticmethod
    def update_scan_frames(self,newValue):
        newValue = int(newValue)
        if self.autoexposure.get() > 0:
            if newValue == 0 or newValue * 10000000 > self.total_exposure:
                newValue = int(self.total_exposure / 10000000)
                if newValue == 0:
                    newValue = 1
                self.scale_scan_frames.set(newValue)
            elif newValue * self.spectrometer.minimum_integration_time_micros < self.total_exposure:
                newValue = int(self.total_exposure / self.spectrometer.minimum_integration_time_micros)
                self.scale_scan_frames.set(newValue)
            newTime = int(self.total_exposure / newValue)
            print('v', newValue)
            print('t: ', newTime)
            #self.scan_time.set(newTime)
            self.scale_scan_time.set(newTime)
        self.scan_frames.set(newValue)
        self.dark_frames.set(newValue)
        self.scale_dark_frames.set(newValue)
        self.total_exposure = int(self.scan_frames.get()) * int(self.scan_time.get())

    #@staticmethod
    def validate_scan_frames(self):
        newValue = self.scan_frames.get()
        if StringIsInt(newValue) and \
           int(newValue) >= 0 and \
           int(newValue) <= 10000:
            self.scale_scan_frames.set(int(newValue))
            self.scale_dark_frames.set(int(newValue))
            self.dark_frames.set(newValue)
        else:
            self.scan_frames.set(self.scale_scan_frames.get())
            self.entry_scan_frames.after_idle(self.entry_scan_frames.config, {'validate': 'focusout', 'validatecommand': self.validate_scan_frames})
        return True


    #@staticmethod
    def update_scan_time(self,newValue):
        newValue = int(newValue)
        if self.autoexposure.get() > 0 and \
           int(self.scan_frames.get()) != 0:
            if newValue * 10000 > self.total_exposure:
                newValue = int(self.total_exposure / 10000)
                print(newValue)
                self.scale_scan_time.set(newValue)
            newFrames = int(self.total_exposure / newValue)
            self.scan_frames.set(newFrames)
            self.dark_frames.set(newFrames)
            self.scale_scan_frames.set(newFrames)
            self.scale_dark_frames.set(newFrames)
        self.scan_time.set(newValue)
        self.spectrometer.integration_time_micros(newValue)
        self.total_exposure = int(self.scan_frames.get()) * int(self.scan_time.get())

    #@staticmethod
    def validate_scan_time(self):
        newValue = self.scan_time.get()
        if StringIsInt(newValue) and \
           int(newValue) >= self.spectrometer.minimum_integration_time_micros and \
           int(newValue) <= 10000000:
            self.scale_scan_time.set(int(newValue))
        else:
            self.scan_time.set(self.scale_scan_time.get())
            self.entry_scan_time.after_idle(self.entry_scan_time.config, {'validate': 'focusout', 'validatecommand': self.validate_scan_time})
        return True


    #@staticmethod
    def update_dark_frames(self,newValue):
        self.dark_frames.set(newValue)

    #@staticmethod
    def validate_dark_frames(self):
        newValue = self.dark_frames.get()
        if StringIsInt(newValue) and \
           int(newValue) >= 1 and \
           int(newValue) <= 10000:
            self.scale_dark_frames.set(int(newValue))
        else:
            self.dark_frames.set(self.scale_scan_frames.get())
            self.entry_dark_frames.after_idle(self.entry_dark_frames.config, {'validate': 'focusout', 'validatecommand': self.validate_dark_frames})
        return True


    #@staticmethod
    def startpause(self):
        self.run_measurement = not self.run_measurement
        self.button_startpause_text.set(self.button_startpause_texts[self.run_measurement])
        self.button_stopdarkness_text.set(self.button_stopdarkness_texts[self.run_measurement])

    #@staticmethod
    def stopdarkness(self):
        if self.run_measurement:
            self.run_measurement = False
            self.button_startpause_text.set(self.button_startpause_texts[self.run_measurement])
            self.button_stopdarkness_text.set(self.button_stopdarkness_texts[self.run_measurement])
            self.message.set('Ready.')
            self.measurement = 0
        else:
            newData = self.spectrometer.intensities()
            count = 1
            self.message.set('Scanning dark frame ' + str(count) + '/' + str(self.dark_frames.get()))
            self.root.update()
            while count < int(self.dark_frames.get()):
                newData = list(map(lambda x,y:x+y, self.spectrometer.intensities(), newData))
                if (count % 100 == 0):
                    print('O', end='', flush=True)
                elif (count % 10 == 0):
                    print('o', end='', flush=True)
                else:
                    print('.', end='', flush=True)
                count += 1
                self.message.set('Scanning dark frame ' + str(count) + '/' + str(self.dark_frames.get()))
                self.root.update()
            self.darkness_correction = list(map(lambda x:x/count, newData))
            self.have_darkness_correction = True
            self.axes.set_ylabel('Intensity [corrected count]')
            self.message.set(str(self.dark_frames.get()) + ' dark frames scanned. Ready.')
            print(str(self.dark_frames.get()) + ' dark frames scanned.')

    #@staticmethod
    def save(self):
        try:
            with open(time.strftime('Snapshot-%Y-%m-%dT%H:%M:%S.dat', time.gmtime()), 'w') as f:
                f.write('# Spectr-O-Mat data format: 2')
                f.write('\n# Time of snapshot: ' + time.strftime(self.timestamp, time.gmtime()))
                f.write('\n# Number of frames accumulated: ' + str(self.measurement))
                f.write('\n# Scan time per exposure [us]: ' + str(self.scan_time.get()))
                if self.have_darkness_correction:
                    f.write('\n# Number of dark frames accumulated: ' + str(self.dark_frames.get()))
                    f.write('\n# Wavelength [nm], dark frame correction data [averaged count]:\n# ')
                    f.write('\n# '.join(map(lambda x,y:str(x)+', '+str(y), self.spectrometer.wavelengths(), self.darkness_correction)))
                    f.write('\n# Wavelength [nm], Intensity [corrected count]:\n')
                else:
                    f.write('\n# Number of dark frames accumulated: None.')
                    f.write('\n# Wavelength [nm], Intensity [count]:\n')
                f.write('\n'.join(map(lambda x,y:str(x)+', '+str(y), self.spectrometer.wavelengths(), self.data)) + '\n')
            self.message.set('Data saved to ' + time.strftime('Snapshot-%Y-%m-%dT%H:%M:%S.dat', time.gmtime()) + '. Ready.')
            print('Data saved to ' + time.strftime('Snapshot-%Y-%m-%dT%H:%M:%S.dat', time.gmtime()))
        except:
            self.message.set('Error while writing ' + time.strftime('Snapshot-%Y-%m-%dT%H:%M:%S.dat', time.gmtime()) + '. Ready.')
            print('Error while writing ' + time.strftime('Snapshot-%Y-%m-%dT%H:%M:%S.dat', time.gmtime()))
        self.root.update()


    #@staticmethod
    def reset(self):
        self.run_measurement = False
        self.button_startpause_text.set(self.button_startpause_texts[self.run_measurement])
        self.button_stopdarkness_text.set(self.button_stopdarkness_texts[self.run_measurement])
        self.darkness_correction = [0.0]*(len(self.spectrometer.wavelengths()))
        self.have_darkness_correction = False
        self.data = [0.0]*(len(self.spectrometer.wavelengths()))
        self.figure.suptitle('No measurement taken so far.')
        self.axes.set_ylabel('Intensity [count]')
        self.measurement = 0
        self.message.set('All parameters reset. Ready.')

    #@staticmethod
    def exit(self):
        sys.exit(0)


    #@staticmethod
    def update_plot(i):
        scan_frames = int(self.scan_frames.get())
        if (self.measurement == scan_frames) or \
           (self.enable_plot.get() > 0):
            self.graph.set_ydata(self.data)
            self.axes.relim()
            self.axes.autoscale_view(True, True, True)


    #@staticmethod
    def measure(self):
        if self.run_measurement:
            scan_frames = int(self.scan_frames.get())
            if (scan_frames > 0):
                self.message.set('Scanning frame ' + str(self.measurement+1) + '/' + str(scan_frames) + '...')
            else:
                self.message.set('Scanning frame...')
            self.root.update()
            newData = list(map(lambda x,y:x-y, self.spectrometer.intensities(), self.darkness_correction))
            if (self.measurement == 0):
                self.data = newData
            else:
                self.data = list(map(lambda x,y:x+y, self.data, newData))
            self.measurement += 1

            plot.suptitle(time.strftime(self.timestamp, time.gmtime()) +
                         ' (sum of ' + str(self.measurement) + ' measurement(s)' +
                         ' with scan time ' + str(self.scan_time.get()) + ' us)')

            if (self.measurement % 100 == 0):
                print('O', end='', flush=True)
            elif (self.measurement % 10 == 0):
                print('o', end='', flush=True)
            else:
                print('.', end='', flush=True)
            if (scan_frames > 0):
                if self.measurement % scan_frames == 0:
                    #print(time.strftime(self.timestamp, time.gmtime()), self.data)
                    if self.autosave.get() != 0:
                        self.save()
                    self.measurement = 0
                    if self.autorepeat.get() == 0:
                        self.run_measurement = False
                        self.button_startpause_text.set(self.button_startpause_texts[self.run_measurement])
                        self.button_stopdarkness_text.set(self.button_stopdarkness_texts[self.run_measurement])
                        self.message.set('Ready.')

        self.root.after(1, self.measure)


def start(self):

        self.T0 = time.time()
        BT.BasicThread.start(self)
        if self.enOut:
            print('%s: Started ON line'%(self.name))
        else:
            print('%s: Started OFF line'%(self.name))
        self.root.mainloop()

def stop(self):
    self.setOutput(0)
    BT.BasicThread.stop(self)

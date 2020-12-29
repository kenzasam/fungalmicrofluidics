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
Client
Plotting of incoming data from spectrometer, using matplotlib animation
"""


__version__ = "1.0.0"

__author__ = "Kenza Samlali"
__copyright__ = "Copyright 2020"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = ""
__status__ = "Production"

# Plotting
import math, time
import sys
import numpy
import matplotlib.animation as animation
import matplotlib.pyplot as plot
plot_animation= None
# client
import socket
import udpControl_objects




class Spectogram():
    def __init__(self,
                TCP,
                enable_plot,
                #xdata,
                #ydata,
                measurement,
                scan_frames,
                scan_time
                ):

        #self.init_plot()
        #print("plot init")

        """Initialize instance variables"""
        #self.wavelengths, self.data,self.measurement == self.scan_frames
        #self.run_measurement = False
        self.enable_plot = enable_plot
        #self.output_file = output_file
        #self.timestamp = '%Y-%m-%dT%H:%M:%S%z'
        #self.wavelengths= xdata
        #self.data = ydata
        self.measurement = measurement
        self.scan_frames = scan_frames
        self.scan_time = scan_time
        self.timestamp = '%Y-%m-%dT%H:%M:%S%z'
        self.TCP=TCP

    def init_plot(self):
        """Initialize plotting subsystem"""
        # Plot setup
        self.figure = plot.figure()
        self.axes = self.figure.gca()
        #self.graph, = self.axes.plot(self.wavelengths, self.data)
        self.graph, = self.axes.plot([], [])
        self.figure.suptitle('No measurement taken so far.')
        self.axes.set_xlabel('Wavelengths [nm]')
        self.axes.set_ylabel('Intensity [count]')
        """Create a FuncAnimation object to make the animation. The arguments are:
        self.figure: the current active figure
        self.animate: function which updates the plot from one frame to the next
        msg_values: our array
        """
        return self.graph,

    '''
    def gen_function(): #fumction checking if new TCP package arrived
        gfdsfh

    '''


    def animate(self,frame):
       object=self.TCP.run()#(nameID='udpSpecPlot', DesIP=IP,RxPort=CLIENT_PORT, callFunc=decodingPayload)
       print 'Decoding now...'
       #print object
       #self.decodingPayload(object) #once full message received
       self.measurement=object['Msr']
       xdata=object['L']
       ydata=object['Dat']
       if i==0:
           return self.init()
       if (self.measurement == self.scan_frames) or \
          (self.enable_plot > 0):
           title='%s sum of %d measurements with integration time %d us' %(time.strftime(self.timestamp, time.gmtime()) , self.measurement, self.scan_time )
           plot.suptitle(title)
           self.graph.set_ydata(ydata)
           self.axes.relim()
           self.axes.autoscale_view(True, True, True)
           print 'alolo'
           return self.graph,


    '''
    def decodingPayload(self, object):

        #Object received from Server (udpControl_objects, threadSpec)
        #In this case, a dictionary d={'Msr':self.measurement,'Dat':self.data}

        print 'Received.'
        self.measurement=object['Msr']
        self.ydata=object['Dat']
        self.xdata=object['L']
        print self.measurement
        print self.xdata
        #return measurement,ydata,xdata
        #self.ydata=self.data[-1][1]
    '''

if __name__== "__main__":
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#
    CLIENT_PORT = 7002 # port to which udpSend package is sent. See ArduBridge.
    IP='127.0.0.1'
    scan_time=1000
    scan_frames=1
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#

    ydata=[]
    xdata=[]
    measurement=0

    udpConsol = False
    if CLIENT_PORT > 1:
        udpConsol = udpControl_objects.udpControl(nameID='udpSpecPlot', DesIP=IP,RxPort=CLIENT_PORT) # callFunc=decodingPayload
        print 'Remote-Consol-Active on port %s\n'%(str(CLIENT_PORT))
    ag=Spectogram(TCP=udpConsol, enable_plot=True, scan_frames=scan_frames, measurement=measurement, scan_time=scan_time)
    #udpConsol.run() #receiving on RxPort and running CallFunc (self.animate) for each payload received
    #self.plot_animation= animation.FuncAnimation(self.figure, self.animate, init_func=ag.init_plot, frames=gen_function, interval=10, blit=True)
    #plot.show()

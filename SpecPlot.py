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
Plotting of incoming data from spectrometer, using matplotlib animation.
TCP Client.
TCP server (ThreadSpec, TCP_Send) sends data (dataframe) to this client.
"""


__version__ = "1.0.0"
__author__ = "Kenza Samlali"
__copyright__ = "Copyright 2020"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = ""
__status__ = "Production"

from optparse import OptionParser
# Plotting
import math, time
import sys
import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plot
plot_animation= None
# TCP client
import socket
import tcpControl as client

class Spectogram(client.tcpControl):
    def __init__(self,
                nameID,
                DesIP,
                RxPort,
                callFunc,
                enable_plot,
                scan_frames,
                scan_time
                ):
        """Initialize TCP client"""
        if RxPort > 1:
            print 'Initiating client.'
            client.tcpControl.__init__(self,nameID=nameID, DesIP=DesIP,RxPort=RxPort, callFunc=callFunc)
            print 'Remote-Consol-Active on port %s\n'%(str(RxPort))
        """Initialize instance variables"""
        #self.run_measurement = False
        self.enable_plot = enable_plot
        #self.output_file = output_file
        self.scan_frames = scan_frames
        self.scan_time = scan_time
        self.timestamp = '%Y-%m-%dT%H:%M:%S%z'
        #init VARIABLES#
        self.ydata = []
        self.ydata2 = []
        self.ydata3 = []
        self.xdata = []
        self.measurement = 0
        ###########
        self.received = False
        self.init_plot()

    def init_plot(self):
        """Initialize plotting subsystem"""
        # Plot setup
        self.figure = plot.figure()
        self.axes = self.figure.gca()
        #self.graph, = self.axes.plot(self.wavelengths, self.data)
        self.graph, = self.axes.plot([], [])
        self.graph2, = self.axes.plot([], [], 'r')
        self.line, = self.axes.plot([], [] ,'r+')
        self.figure.suptitle('No measurement taken so far.')
        self.axes.set_xlabel('Wavelengths [nm]')
        self.axes.set_ylabel('Intensity [count]')

    def animate(self,i): #,frame
       #object=self.TCP.run()#(nameID='udpSpecPlot', DesIP=IP,RxPort=CLIENT_PORT, callFunc=decodingPayload)
       #print 'Decoding now...'
       #print object
       #self.decodingPayload(object) #once full message received
       #self.measurement=object['Msr']
       #xdata=object['L']
       #ydata=object['Dat']
       '''
       if i==0:
           print 'lll'
           self.graph.set_data(self.xdata,self.ydata)
           #return self.init()
       '''
       if (self.measurement == self.scan_frames) or \
          (self.enable_plot > 0):
           title='%s sum of %d measurements with integration time %d us' %(time.strftime(self.timestamp, time.gmtime()) , self.measurement, self.scan_time )
           plot.suptitle(title)
           self.graph.set_data(self.xdata, self.ydata)
           #self.graph.set_ydata(self.ydata)

           #plot peaks
           ind = [i for i, item in enumerate(self.ydata) if item in self.ydata2]
           peakwvl = [self.xdata[i] for i in ind]
           self.graph2.set_data(peakwvl, self.ydata2)
           for i,j in zip(xtemp, self.ydata2):
               self.graph2.annotate(str(j),xy=(i,j+0.5))
           print(peakwvl)
           #plot treshold
           #self.line.set_data(self.xdata, self.ydata3)

           self.axes.relim()
           self.axes.autoscale_view(True, True, True)
           #return self.graph,
           return (self.graph, self.graph2, self.line)

    def decodingPayload(self, object):
        """Object received from Server (tcpSend, threadSpec)
        In this case, a dictionary d={'Msr':self.measurement,'Dat':self.data}"""
        self.received == True
        #print 'Received.',
        self.measurement=object['Msr']
        #self.scan_frames=object['Fr']
        self.ydata=object['Dat']
        self.xdata=object['L']
        if 'Peaks' in object:
            self.ydata2=object['Peaks']
        if 'Treshold' in object:
            self.ydata3=object['Treshold']
        #self.peaks=object['Peaks']
        #print 'Msrmt #'
        #print self.measurement
        #print self.ydata

if __name__== "__main__":
    #\\\\\\\\\\\\\\\\USER SET VARIABLES\\\\\\\\\\\\\\\\\#
    PLOT_EN = True # Allow plotting
    CLIENT_PORT = 7002 # Client port to which udpSend package is sent. See ArduBridge.
    IP = '127.0.0.1' # Client ip adress to which udpSend package is sent. See ArduBridge.
    SCANTIME = 1000 # The integration time in us.
    SCANFRAMES = 1 # The total nr of measurements/frames that will be summed.
    VERSION = '1.0.0' # version
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#
    print 'GUI: Protocol GUI Ver:%s'%(VERSION)
    print 'Copyright: Kenza Samlali, 2020'

    """Command line option parser"""
    parser = OptionParser()
    parser.add_option('-i', '--ip', dest='ip', help='Client IP address', type='string', default=IP)
    parser.add_option('-c', '--port', dest='port', help='Remote port to send the commands', type='int', default=CLIENT_PORT)
    parser.add_option('-t', '--scantime', dest='scantime', help='Integration time of spectrometer. See ArduBridge', type='int', default=SCANTIME)
    parser.add_option('-f', '--frames', dest='frames', help='Number of scan frames to sum for each experiment. See ArduBridge', type='int', default=SCANFRAMES)
    parser.add_option('-p', '--plot', dest='plot', help='Enable plotting', type='int', default=PLOT_EN)
    (options, args) = parser.parse_args()

    """Spectogram class Instance"""
    ag=Spectogram(nameID='tcpSpecPlot', DesIP=options.ip, RxPort=options.port, callFunc=Spectogram.decodingPayload, enable_plot=options.plot, scan_frames=options.frames, scan_time=options.scantime)
    #ag=Spectogram(TCP=udpConsol, enable_plot=True, scan_frames=scan_frames, measurement=measurement, scan_time=scan_time)
    #ag=Spectogram(nameID='udpSpecPlot', DesIP=IP,RxPort=CLIENT_PORT, callFunc=Spectogram.decodingPayload,enable_plot=True, scan_frames=scan_frames, scan_time=scan_time) # , measurement=measurement

    """Start client thread"""
    client.tcpControl.start(ag)

    """Create a FuncAnimation object to make the animation. The arguments are:
           ag.figure: the current active figure
           ag.animate: function which updates the plot from one frame to the next. Is looped continuously.
    """
    print 'TCP plotting thread started succesfully. Waiting for data from client.'
    #if ag.received==True: #we should check this conditions beforehand. But I tried and somehow the plot remains empty.....
    plot_animation= animation.FuncAnimation(ag.figure, ag.animate, blit=False) #frames=gen_function, init_func=self.init_plot
    plot.show()
    #self.plot_animation= animation.FuncAnimation(self.figure, self.animate, init_func=ag.init_plot, frames=gen_function, interval=10, blit=True)

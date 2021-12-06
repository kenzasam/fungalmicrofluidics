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
Uses TCP Client.
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
import matplotlib.patches as patches

plot_animation = None
# TCP client
import socket
from . import tcpControl as client

class Spectogram(client.tcpControl):
    def __init__(self,
                nameID,
                DesIP,
                RxPort,
                callFunc,
                enable_plot,
                enable_sp
                ):
        """Initialize TCP client"""
        if RxPort > 1:
            print('Initiating client.')
            client.tcpControl.__init__(self,nameID=nameID, DesIP=DesIP,RxPort=RxPort, callFunc=callFunc)
            print('Remote-Consol-Active on port {}\n'.format(str(RxPort)))
        """Initialize instance variables"""
        self.enable_plot = enable_plot
        self.enable_sp = enable_sp
        self.timestamp = '%Y-%m-%dT%H:%M:%S%z'
        #init VARIABLES#
        self.ydata = [] 
        self.ydata1 = [] # denoised. See decoding.
        self.ydata2 = [] # peaks. See decoding.
        self.xdata2 = [] # peaks wavelength. See decoding.
        self.ydata3 = [0,0,0,0] # Gating. See decoding. [self.SPS.gateI,self.SPS.gateL]
        self.xdata = []
        self.measurement = 0
        ###########
        self.received = False
        self.init_plot()

    def init_plot(self):
        """Initialize plotting subsystem"""
        # Plot setup
        self.figure, (self.ax1, self.ax2) = plot.subplots(2, sharex='col', sharey='row')
        #raw signal
        self.line1, = self.ax1.plot([], [])
        self.graph = self.line1
        if self.enable_sp == True:
            #denoised signal
            self.line2, = self.ax2.plot([], [], 'b')
            #gating area
            rect = patches.Rectangle((self.ydata3[2], self.ydata3[0]), self.ydata3[3]-self.ydata3[2], self.ydata3[1]-self.ydata3[0], fc='y', alpha=0.5)
            self.area = self.ax2.add_patch(rect) 
            self.graph = [self.line1, self.line2, self.area]
        self.figure.suptitle('No measurement taken so far.')
        '''
        for ax in [self.ax1, self.ax2]:
            ax.set_ylim(0, 10000)
            ax.set_xlim(200, 1000)
            #ax.grid()
        '''
        self.ax1.set_xlabel('Wavelengths [nm]')
        self.ax1.set_ylabel('Intensity [count]')
        
    def animate(self,i):
        if (self.enable_plot > 0): #(self.measurement == self.scan_frames) or \
            title = '%s /n Live Spectral Measurements' %(time.strftime(self.timestamp, time.gmtime()))
            self.figure.suptitle(title)
            self.line1.set_data(self.xdata, self.ydata)
            if self.enable_sp == True:
                #DENOISED SIGNAL
                self.line2.set_data(self.xdata, self.ydata1)
                #GATE
                x0 = self.ydata3[2]
                y0 = self.ydata3[0]
                w = self.ydata3[3]-self.ydata3[2] 
                h = self.ydata3[1]-self.ydata3[0]
                self.area.set_bounds(x0, y0, w, h)
            for ax in [self.ax1, self.ax2]:
                ax.relim()
                ax.autoscale_view(True, True, True)
            return self.graph

    def decodingPayload(self, object):
        '''Object received from Server (tcpSend, threadSpec)
        In this case, a dictionary d={'Msr':self.measurement,'Dat':self.data}
        '''
        self.received == True
        self.measurement=object['Msr']
        self.ydata = object['Dat']
        self.xdata = object['L']
        if 'Peak_wvl' in object:
            self.xdata2 = object['Peak_wvl']
        if 'Peak_int' in object:
            self.ydata2 = object['Peak_int']
        if 'Gate' in object:
            self.ydata3 = object['Gate']
        if 'DatDn' in object:
            self.ydata1 = object['DatDn']

if __name__== "__main__":
    #\\\\\\\\\\\\\\\\USER SET VARIABLES\\\\\\\\\\\\\\\\\#
    PLOT_EN = True # Allow plotting
    PROC_EN = True # Allow plotting
    CLIENT_PORT = 7002 # Client port to which udpSend package is sent. See ArduBridge.
    IP = '127.0.0.1' # Client ip adress to which udpSend package is sent. See ArduBridge.
    VERSION = '1.0.0' # version
    #\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\#
    print('GUI: Protocol GUI Ver:'+VERSION)
    print('Copyright: Kenza Samlali, 2020-2021')

    """Command line option parser"""
    parser = OptionParser()
    parser.add_option('-i', '--ip', dest='ip', help='Client IP address', type='string', default=IP)
    parser.add_option('-c', '--port', dest='port', help='Remote port to send the commands', type='int', default=CLIENT_PORT)
    parser.add_option('-p', '--plot', dest='plot', help='Enable plotting', type='int', default=PLOT_EN)
    parser.add_option('-s', '--sproc', dest='proc', help='Enable signal processing', type='int', default=PROC_EN)
    (options, args) = parser.parse_args()

    """Spectogram class Instance"""
    ag=Spectogram(nameID='tcpSpecPlot', DesIP=options.ip, RxPort=options.port, callFunc=Spectogram.decodingPayload, enable_plot=options.plot, enable_sp=options.proc)
   
    """Start client thread"""
    client.tcpControl.start(ag)
    print('TCP plotting thread started succesfully. Waiting for data from client.')

    """Create a FuncAnimation object to make the animation. The arguments are:
           ag.figure: the current active figure
           ag.animate: function which updates the plot from one frame to the next. Is looped continuously.
    """
    plot_animation= animation.FuncAnimation(ag.figure, ag.animate, blit=True)
    plot.show()

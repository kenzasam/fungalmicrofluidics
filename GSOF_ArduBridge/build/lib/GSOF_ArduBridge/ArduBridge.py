#!/usr/bin/env python
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

Generate the main object to communicate with an arduino the runs the GSOF-Ardubridge firmware.
"""

__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = ["James Perry"]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import sys
from GSOF_ArduBridge import BridgeSerial
from GSOF_ArduBridge import ArduAnalog
from GSOF_ArduBridge import ArduGPIO
from GSOF_ArduBridge import ArduI2C

class ArduBridge():
    def __init__(self, COM='COM9', baud=115200*2):

        version = 'v1.0 running on Python %s'%(sys.version[0:5])
        print('GSOF_ArduBridge %s'%(version))
        self.ExtGpio = [0,0]
        self.COM  = COM
        self.comm = BridgeSerial.ArduBridgeComm( COM=COM, baud=baud )
        self.gpio = ArduGPIO.ArduBridgeGPIO( bridge=self.comm )
        self.an   = ArduAnalog.ArduBridgeAn(bridge=self.comm )
        self.i2c  = ArduI2C.ArduBridgeI2C( bridge=self.comm )#, v=True )

    def OpenClosePort(self, val):
        if type(val) == str:
            if val == 'open':
                val = 1
            else:
                val = 0
        self.comm.OpenClosePort(val)
        if val != 0:
            self.GetID()

    def Reset(self):
        self.comm.sendReset()
        self.comm.uart_flush()
        self.GetID()

    def GetID(self):
        self.comm.send([ord('?')])
        reply = self.comm.receive(1)
        if reply[0] != -1:
            s = ''
            ACK = 1
            N = reply[1][0]
            while (ACK != -1) and (N > 0):
                reply = self.comm.receive(1)
                ACK = reply[0]
                if ACK != -1:
                    N -= 1
                    #print(chr(reply[1][0]))
                    s += chr(reply[1][0])
            s += '\n'
            print('%s'%(s))
#            if reply[0] == 1:
#                print('Got reply\n')
        else:
            print('No reply\n')

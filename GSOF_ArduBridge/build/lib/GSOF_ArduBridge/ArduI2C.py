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

Class to access the Arduino-Bridge I2C bus.
This class is using the BridgeSerial class object to communicate over serial
with the GSOF-Arduino-Bridge firmware.
The packet has a binary byte based structure
To write:
<'2'>,<'A'>,<DEV#>,<'L'>,<n+1>,<'W'>,<REG#>,<DAT1>,<DAT2>...<DATn>
e.g, to write to device 0x14 starting as register 0x10 the values 0,1,2 use:
['2', 'A', 0x14, 'L', 4, 'W', 0x10, 0x00, 0x01, 0x02]

To read:
<'2'>,<'A'>,<DEV#>,<'L'>,<1>,<'w'>,<REG#>
<'2'>,<n>,<'R'>

e.g, to read fromto device 0x14 starting as register 0x10, 3 bytes use:
['2', 'A', 0x14, 'L', 1, 'w', 0x10]
followed by:
['2', 'L', 3, 'R']

note:'2' I2C packet header
     'W' write
     'w' write-restart
     'R' read
     'A' device-address
     'L' data lenght
"""

__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import time
from GSOF_ArduBridge import BridgeSerial
from GSOF_ArduBridge import CON_prn

class ArduBridgeI2C():
    def __init__(self, bridge=False, v=False):
        self.v = v
        self.comm = bridge
        self.RES = {1:'OK', -1:'ERR'}

        #I2C protocol command
        self.I2C_PACKET_ID = ord('2')
        self.CMD_I2C_ADDRESS = ord('A')
        self.CMD_I2C_LENGTH = ord('L')
        self.CMD_I2C_WRITE_RESTART = ord('w')
        self.CMD_I2C_WRITE = ord('W')
        self.CMD_I2C_READ_RESTART = ord('r')
        self.CMD_I2C_READ = ord('R')

        self.ERROR_NONE	= ord('N')
        self.ERROR_UNESCAPE = ord('U')
        self.ERROR_LENGTH = ord('L')
        self.ERROR_READ = ord('R')
        self.ERROR_WRITEDATA = ord('W')
        self.ERROR_SENDDATA = ord('S')

        self.ERROR = {self.ERROR_NONE:'OK',
                      self.ERROR_UNESCAPE:'UNESCAPE',
                      self.ERROR_LENGTH:'LENGTH',
                      self.ERROR_READ:'READ',
                      self.ERROR_WRITEDATA:'WRITE-DATA',
                      self.ERROR_SENDDATA:'SEND-DATA'}

    def writeRaw(self, dev, vByte):
        vDat = [self.I2C_PACKET_ID,   #I2C packet-ID
                self.CMD_I2C_ADDRESS, #next byte is the I2C device-address
                dev,                  #DEV#
                self.CMD_I2C_LENGTH,  #Next byte is the data length
                len(vByte),           #Data length
                self.CMD_I2C_WRITE   #Next bytes should be sent as is to the I2C device
                ]+vByte                #data-vector
        
        self.comm.send(vDat)
        reply = self.comm.receive(1)
  
        if self.v:
            if reply[0] != 0:      #did we received a byte
                res = reply[1][0]  #if yes, read the result
                CON_prn.printf('I2C-WR: Dev-0x%02x, Reg%d - %s', par=(dev, reg, self.ERROR[res]), v=True)
        return reply

    def writeRegister(self, dev, reg, vByte):
        vDat = [self.I2C_PACKET_ID,   #I2C packet-ID
                self.CMD_I2C_ADDRESS, #next byte is the I2C device-address
                dev,                  #DEV#
                self.CMD_I2C_LENGTH,  #Next byte is the data length (including the register#)
                len(vByte) +1,        #Data length
                self.CMD_I2C_WRITE,   #Next bytes should be sent as is to the I2C device
                reg] +vByte           #REG# +data-vector
        
        self.comm.send(vDat)
        reply = self.comm.receive(1)
  
        if self.v:
            if reply[0] != 0:      #did we received a byte
                res = reply[1][0]  #if yes, read the result
                CON_prn.printf('I2C-WR: Dev-0x%02x, Reg%d - %s', par=(dev, reg, self.ERROR[res]), v=True)
        return reply

    def readRegister(self, dev, reg, N):
        vHdr = [self.I2C_PACKET_ID,         #I2C packet-ID
                self.CMD_I2C_ADDRESS,       #next byte is the I2C device-address
                dev,                        #DEV#
                self.CMD_I2C_LENGTH,        #Next byte is the data length (including the register#)
                1,                          #Data length
                self.CMD_I2C_WRITE_RESTART, #Next bytes should be sent as is to the I2C device
                reg]

        vRd  = [self.I2C_PACKET_ID,         #I2C packet-ID
                self.CMD_I2C_LENGTH,        #Next byte is the data length (including the register#)
                N,                          #N bytes to read
                self.CMD_I2C_READ]          #Start the read sequence

        self.comm.send(vHdr +vRd)
        reply = self.comm.receive(1)        #1st byte is the ACK for the register write
        if (reply[0] != 0) and (reply[0] != -1):
            reply = self.comm.receive(1)        #2nd byte is how many bytes where read
            if reply[0] != 0:
                n = reply[1][0]
                reply = self.comm.receive(n)    #Read n bytes
                if reply[0] != 0:
                    val = reply[1]
                    CON_prn.printf('I2C-RD: Dev-0x%02x, Reg%d, Dat %s ', par=(dev, reg, str(val)), v=self.v)
                    return val
        CON_prn.printf('I2C-RD: Dev%d, Reg%d - Error', par=(dev, reg), v=self.v)
        return -1

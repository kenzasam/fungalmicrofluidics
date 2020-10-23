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

Class to access the external-GPIO connected to the Arduino-Bridge via I2C.
This class is using the BridgeSerial class object to generate I2C-Bus cycles
over with the Arduino-Bridge hardware.
"""

__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

from GSOF_ArduBridge import CON_prn

class Max3700ExtGPIO():
    def __init__(self, i2c=False, devID=0x00, pinZeroOffset=8, v=False):
        self.ID = 'MAX3700-ID 0x%02x'%(devID)
        self.v = v
        self.i2c = i2c
        self.devID = devID
        self.portRegOffset = 0x44
        self.pinRegOffset = 0x24
        self.bankModeOffset = 0x09
        self.pinZeroOffset = pinZeroOffset
        
        self.modeReg = 0x04
        self.RES = {1:'OK', 0:'ERR', -1:'ERR'}
        self.DIR = {0:'Active-Low', 1:'Active-High', 2:'Input without pullup', 3:'Input + pullup'}
        self.MODE = {0:'Shutdown', 1:'Normal'}
        self.tDet = {0:'Disable', 1:'Enable'}

    def modeSet(self, mode=1, transitionDetection=0):
        #mode: 0 - Shutdown; 1 - Normal operation
        #transitionDetection: 0 - Disable; 1 - Enable
        if mode != 0:
            mode = 1
        val = mode
        val |= (transitionDetection&0x1)<<7
        reply = self.i2c.writeRegister(self.devID, self.modeReg, [mode])
        if self.v:
            CON_prn.printf('%s: MODE-Set: %s',
                           par=(self.ID, self.RES[reply[0]]),
                           v=True)
        return reply[0]

    def modeGet(self):
        reply = self.i2c.readRegister(self.devID, self.modeReg, 1)
        if self.v:
            if reply != -1:
                mode = reply[0]&1
                td = (reply[0]>>7)&1
                CON_prn.printf('%s: MODE-Get: %s, Transition-Detection: %s',
                               par=(self.ID, self.MODE[mode], self.tDet[td]),
                               v=True)
        return reply

    def bankModeSet(self, val=0x55, B=0, N=7):
        if (B+N) > 7:
            N = 7-B #Set upto 7 banks
        reply = self.i2c.writeRegister(self.devID, self.bankModeOffset+B, [val]*N)
        CON_prn.printf( '%s: bankMode Set: %s', par=(self.ID, self.RES[reply[0]]) )
        return reply

    def bankModeGet(self, B=0, N=7):
        if (B+N) > 7:
            N = 7-B #Get upto 7 banks
        reply = self.i2c.readRegister(self.devID, self.bankModeOffset+B, N)
        CON_prn.printf( '%s: bankMode: %s', par=(self.ID, str(reply)) )
        return reply

##    def pinMode(self, pin, mode):
##        """
##        Set the mode of the specific pin# on the MX3700
##        """
##        reg = pin/4 +self.pinModeOffset
##        bitField = pin%4
##        vDat = [ord('D'), pin, mode]
##        self.comm.send(vDat)
##        reply = self.comm.receive(1)
##        if self.v:
##            CON_prn.printf('DIR%d: %s - %s', par=(pin, self.DIR[mode], self.RES[reply[0]]), v=True)
##        return reply[0]

    def pinWrite(self, pin, valList):
        """
        Set the state of the specific pin(s)# on the MX3700
        """
        if type(valList) == int:
            valList = [valList]
        for val in valList:
            if (val != 0):
                val = 1
            pinReg = self.pinRegOffset +self.pinZeroOffset +pin
            reply = self.i2c.writeRegister(self.devID, pinReg, [val])
            CON_prn.printf('%s: PIN%d-Set: %d - %s', par=(self.ID, pin, val, self.RES[reply[0]]), v=self.v)
            pin += 1
        return reply[0]

    def portWrite(self, port, val):
        """
        Set the state of the specific port# on the MX3700
        """
        portReg = self.portRegOffset +self.pinZeroOffset +port
        reply = self.i2c.writeRegister(self.devID, portReg, [val&0xff])
        if self.v:
            CON_prn.printf('%s: POPT%d-Set: %s', par=(self.ID, port, self.RES[reply[0]]), v=True)
        return reply[0]

    def pinRead(self, pinList):
        """
        Read the state of the specific pin(s)# on the MX3700
        """
        if type(pinList) == int:
            pinList = [pinList]
        result = []
        for pin in pinList:
            pinReg = self.pinRegOffset +self.pinZeroOffset +pin
            reply = self.i2c.readRegister(self.devID, pinReg, 1)
            if reply != -1:
                CON_prn.printf('%s: PIN%d = %d', par=(self.ID, pin, reply[0]), v=self.v)
                result.append(reply[0])
            else:
                CON_prn.printf('%s: PIN%d-Get: Error', par=(self.ID, pin), v=self.v)
                result.append(-1)
        return result
        
    def portRead(self, port):
        """
        Read the state of the specific port# on the MX3700
        """
        portReg = self.portRegOffset +self.pinZeroOffset +port
        reply = self.i2c.readRegister(self.devID, portReg, 1)
        if reply != -1:
            CON_prn.printf('%s: PORT%d = 0x%02x (%s)', par=(self.ID, port, reply[0], bin(reply[0])), v=self.v)
            return reply[0]
        CON_prn.printf('%s: PORT%d-Get: Error', par=(self.ID, port), v=self.v)
        return -1

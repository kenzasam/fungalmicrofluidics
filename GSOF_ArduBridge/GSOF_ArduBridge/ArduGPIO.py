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

Class to access the Arduino-Bridge digital inputs and outputs.
This class is using the BridgeSerial class object to communicate over serial
with the GSOF-Arduino-Bridge firmware.
The packet has a binary byte based structure
byte0 - 'D' to set pin direction, 'I' to read pin state, 'O' to set pin state
        'S' to set the servo control value (Not supported in all firmwares)
byte1 - pin bumber (binary-value)
byte2 - pin-value (binary-value) only for digital-out command
"""

__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = ["James Perry"]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import time
from GSOF_ArduBridge import BridgeSerial
from GSOF_ArduBridge import CON_prn

class ArduBridgeGPIO():
    def __init__(self, bridge=False, v=False):
        self.v = v
        self.comm = bridge
        self.RES = {1:'OK', 0:'ERR' , -1:'ERR'}
        self.DIR = {1:'IN', 0:'OUT'}

    def pinMode(self, pin, mode):
        if (mode != 0):
            mode = 1
        if (pin < 0x1b):
            vDat = [ord('D'), pin, mode]
            #print(str(vDat))
            self.comm.send(vDat)
        reply = self.comm.receive(1)
        #print(reply)
        CON_prn.printf('DIR%d: %s - %s', par=(pin, self.DIR[mode], self.RES[reply[0]]), v=self.v)
        return reply[0]

    def digitalWrite(self, pin, val):
        val = int(val)
        if (val != 0):
            val = 1
        if (pin < 0x1b):
            vDat = [ord('O'), pin, val]
            self.comm.send(vDat)
        reply = self.comm.receive(1)
        CON_prn.printf('DOUT%d: %d - %s', par=(pin, val, self.RES[reply[0]]), v=self.v)
        return reply[0]

    def servoWrite(self, val):
        val = int(val)
        vDat = [ord('S'), val]
        self.comm.send(vDat)
        reply = self.comm.receive(1)
        CON_prn.printf('SERVO: %d - %s', par=(val, self.RES[reply[0]]), v=self.v)
        return reply[0]

    def pinPulse(self, pin, onTime):
        """
        Pulse the the specific pin# on the arduino GPO
        """
        self.digitalWrite(pin, 1)
        time.sleep(onTime)
        self.digitalWrite(pin, 0)
        return 1

    def digitalRead(self, pin):
        if (pin < 0x1b):
            vDat = [ord('I'), pin]
            self.comm.send(vDat)
        reply = self.comm.receive(1)
        if reply[0]:
            val = reply[1][0]
            CON_prn.printf('DIN%d: %d', par=(pin, val), v=self.v)
            return val
        CON_prn.printf('DIN%d: Error', par=(pin), v=self.v)
        return -1

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

General UDP transmitter.
1. Send a any type of list to the specific ip/port.
"""

__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = []
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

import socket

class udpSend():
    def __init__(self, nameID='', DesIP='127.0.0.1', DesPort=6000):
        self.nameID = str(nameID)
        self.DesIP = str(DesIP)
        self.DesPort = int(DesPort)
        #Datagram (UDP) socket
        try:
            self.udpTx = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            print('%s: Ready to send to %s:%d\n'%(nameID, self.DesIP, self.DesPort))
        except socket.error as msg :
            print('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
                 
    def Send(self, s):
        buf = str(bytearray(str(s)))
        self.udpTx.sendto( buf,(self.DesIP, self.DesPort) )

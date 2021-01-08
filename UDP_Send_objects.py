"""
Copyright, 2020, Kenza Samlali
"""

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
Script to build a SERVER, TCP networking protocol.
Compared to GSOF_ArduBridgeV1 udupControl, this script builds a server that can
receive Object as payload/message, and not just strings. It's TCP and not UDP.
"""
__version__ = "1.0.0"

__author__ = "Kenza Samlali"
__copyright__ = "Copyright 2020"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = ""
__status__ = "Production"

import socket, time, pickle, threading

'''
Define a Header size. The header is a string of characters describing the content that follows.
In this case, it will contain len(msg) (number). Assuming the message length is smaller than 100mil,
a headersize of 10 should do the ElectrodeGpioStack'''

HEADERSIZE = 10

class udpSend():
    def __init__(self, nameID='', DesIP='127.0.0.1', DesPort=0):
        self.nameID = str(nameID)
        self.DesIP = str(DesIP)
        self.DesPort = int(DesPort)
        #We're now creating a Server socket
        try:
            self.udpTx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.udpTx.bind((self.DesIP, self.DesPort))
            #c, addr = self.udpTx.accept()
            print '%s: TCP Ready to send to %s:%d\n'%(nameID, self.DesIP, self.DesPort)

            #    self.c, self.addr = self.udpTx.accept()
        except socket.error, msg :
            print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    '''
    def Connect(self):
        self.udpTx.listen(5) #stream 5 at a time
        print 'Listening for client...'
        print 'Please run spec viewer.'
        c, addr = self.udpTx.accept()
        print 'connected...'
    '''
    def Send(self, d,c):
        '''
        Starts the TCP/IP server.
        Using this function, you can send objects as a message to your client.
        '''
        '''
        self.active = True
        self.Thread = threading.Thread(target=self.run(d))
        self.Thread.start()
        '''

        self.active = True
        self.run(d,c)

    def run(self, data, client):
        global HEADERSIZE
        self.running = True
        #while self.active:
        self.udpTx.settimeout(10)
        try:
            #print 'listening...'
            #self.udpTx.listen(5) #stream 5 at a time
            #print 'waiting for connection...'
            #c, addr = self.udpTx.accept()
            #print d
            msg = pickle.dumps(data) #converts object into bytes
            lmsg='{:<10}'.format(str(len(msg))) #10=HEADERSIZE
            msg = str(lmsg)+msg #py3:  bytes(f"{len(msg):<{HEADERSIZE}}", 'utf-8')+msg
            # adding a header to our payload.
            # The header contains the length in bytes of our payload.
            # This will  help us adjust to the buffer size. (See client)
            #print msg
            client.send(msg)
            print 'Data sent to %s:%d\n'%(self.DesIP, self.DesPort)
            #self.udpTx.close()
        except socket.timeout:
            msg=''
        self.running=False

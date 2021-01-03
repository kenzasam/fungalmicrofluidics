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
Script to build a Client, TCP networking protocol.
Compared to GSOF_ArduBridgeV1 udupControl, this script builds a CLIENT that can
receive Object as payload/message, and not just strings. It's a continuous streaming TCP protocol.
# AF_INET == ipv4
# SOCK_STREAM == TCP
"""
__version__ = "1.0.0"

__author__ = "Kenza Samlali"
__copyright__ = "Copyright 2020"
__credits__ = [""]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = ""
__status__ = "Production"

import socket, sys, time, threading, pickle

HEADERSIZE=10

class udpControl():
    def __init__(self, nameID='',  DesIP='127.0.0.1', RxPort=7010, callFunc=False): # callFunc=False
        self.nameID = str(nameID)
        self.callFunc = callFunc
        self.RxPort = int(RxPort)
        self.DesIP=str(DesIP)
        self.active = False
        self.running = False
        ok = True
        #We're now creating a socket for the Client
        try:
            self.udpRx = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error, msg :
            print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            ok = False

        if ok:
            # Bind socket to local host and port
            try:
                #self.udpRx.setblocking(1)
                self.udpRx.connect((self.DesIP,self.RxPort))
                #self.udpRx.bind(('', self.RxPort))
            except socket.error , msg:
                print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
                ok = False
            print '%s: Ready on port %d\n'%(nameID, self.RxPort)
            self.active = True
            #self.run()
            #''' #If you wish to thread, keep this CODE
            self.active = True
            self.Thread = threading.Thread(target=self.run)
            self.Thread.start()
            #'''

    def update(self, object):
        if self.callFunc != False:
            self.callFunc(self,object)

    def run(self):
        global HEADERSIZE
        #print 'TCP-running...'
        full_msg = b''
        new_msg = True
        print 'out of While'
        while True: #loop forever
            self.running = True
            #while self.active==True:
            #print 'TCP-running...'
            #self.udpRx.settimeout(1)
            #try:
            print 'hello, receiving data'
            msg= self.udpRx.recv(512)
            #print 'message:'
            #print msg
            if new_msg:
                if msg=='':
                    continue
                else:
                    #print("new msg len:",msg[:HEADERSIZE])
                    msglen = int(msg[:HEADERSIZE])
                    new_msg = False
            #py3 print(f"full message length: {msglen}")
            #print 'full message length: %d' %(msglen)
            full_msg += msg
            #print len(full_msg)
            if len(full_msg)-HEADERSIZE == msglen:
                print "Full msg recvd"
                #print(full_msg[HEADERSIZE:])
                #print(pickle.loads(full_msg[HEADERSIZE:]))
                msg_obj=pickle.loads(full_msg[HEADERSIZE:])
                #print msg_obj
                #return msg_obj
                self.update(msg_obj)
                new_msg = True
                full_msg = b''
                print 'thats it'
        '''
        except socket.timeout:
            full_msg=b''
        '''
        self.running = False
        print 'TCP-stopped...'

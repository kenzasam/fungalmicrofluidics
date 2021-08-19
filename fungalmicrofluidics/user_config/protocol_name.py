"""
Copyright, 2020, Guy  Soffer, Kenza Samlali
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
    along with Foobar.  If not, see <https://www.gnu.org/licenses/>.
"""
"""
## Protocol by Kenza Samlali
## June 2020: V1.0
"""

try:
    from GSOF_ArduBridge import threadElectrodeSeq
except ImportError:
    threadElectrodeSeq = False
    class dummyThread():
        def __init__(self, nameID):
            self.name = nameID
from GSOF_ArduBridge import threadBasic as bt
import time, copy
import sys
import os

class Protocol(bt.BasicThread):

    def __init__(self, setup=False, nameID='DROP', Period=1, incTime=2*60):
        #super(StoppableThread, self).__init__()
        bt.BasicThread.__init__(self, Period=Period, nameID=nameID)
        self.setup = setup
        self.reset()
        self.incTime = incTime #for DMF protocol working with incubation times

    def reset(self):
        self.pause()

    def is_alive(self):
        if self.isAlive():
            return True
        else:
            return False

class Setup():
    def __init__(self, ExtGpio, gpio, chipViewer, Pumps, Spec, SpecSP):
        self.init_pumps(Pumps=Pumps)
        self.init_spec(Spec=Spec, SpecSP=SpecSP)
        self.init_elecs(gpio=gpio,ExtGpio = ExtGpio, chipViewer = chipViewer)

    def init_spec(self, Spec, SpecSP): #setup.init_spec(Spec, SpecSP)
        """
        Initializing spectrometer thread.
        """
        print('>>>  <<<')
        print('>>>  Checking spectrometer  <<<')
        if (Spec is None):
            print("Spectrometer thread not found! No spectrometer initiated. Spectomer thread is needed for this protocol.")
        else:
            self.spec=Spec
            print("ok.")

        if (SpecSP is None):
            print("Spectrometer signal processing thread not found! No spectrometer initiated. Spectomer thread is needed for this protocol.")
        else:
            self.specsp=SpecSP
            print("ok.")

    def init_pumps(self, Pumps):
        """
        Initializing NeMESYS syringe pump thread.
        """
        print('>>>  <<<')
        print('>>>  Checking syringe pumps  <<<')
        if (Pumps is None):
            print("Pump bridge not found! No syringe pumps initiated. Syringe pumps are needed for this protocol.")
        else:
            self.nem = Pumps
            print("ok.")

    def init_elecs(self,gpio, ExtGpio,chipViewer): 
        """
        Initializing electrode sequences.
        """
        self.gpio = gpio
        self.ExtGpio = ExtGpio
        self.chipViewer = chipViewer
        self.seq = {} #initializes dictionary, which is an array of associations; returns associated value when a value is inputted
        self.categoryDict = {}

        # \/ ** START OF SEQUENCE ** \/
        seqCategory = 'Sorting'  #<-- EDIT THIS
        seqName = 'S1'  #<-- EDIT THIS
        seqDesc = ''  #<-- EDIT THIS
        b=[[98]]
        seqList = b # <-- Electrodes 1 and 2 actuated at same time. 3 actuated after 1 and 2.
        seqOnTime= 0.9 # <-- How long is the electrode actuated [Sec]
        seqPeriod= 1 # <-- Keep this at least 0.2 seconds above onTime [Sec]

        self.seqAdd(seqCategory, seqName, seqDesc, seqList, seqPeriod, seqOnTime, ExtGpio, chipViewer) #DON'T EDIT
        # /\ **  END OF SEQUENCE  ** /\
        # \/ ** START OF SEQUENCE ** \/
        seqCategory = 'Sorting'  #<-- EDIT THIS
        seqName = 'S2'  #<-- EDIT THIS
        seqDesc = ''  #<-- EDIT THIS
        b=[[75]]
        seqList = b # <-- Electrodes 1 and 2 actuated at same time. 3 actuated after 1 and 2.
        seqOnTime= 0.7 # <-- How long is the electrode actuated [Sec]
        seqPeriod= 1 # <-- Keep this at least 0.2 seconds above onTime [Sec]

        self.seqAdd(seqCategory, seqName, seqDesc, seqList, seqPeriod, seqOnTime, ExtGpio, chipViewer) #DON'T EDIT
        # /\ **  END OF SEQUENCE  ** /\
        # \/ ** START OF SEQUENCE ** \/
        seqCategory = 'Sorting'  #<-- EDIT THIS
        seqName = 'S3'  #<-- EDIT THIS
        seqDesc = ''  #<-- EDIT THIS
        b=[[]]
        seqList = b # <-- Electrodes 1 and 2 actuated at same time. 3 actuated after 1 and 2.
        seqOnTime= 0.7 # <-- How long is the electrode actuated [Sec]
        seqPeriod= 1 # <-- Keep this at least 0.2 seconds above onTime [Sec]

        self.seqAdd(seqCategory, seqName, seqDesc, seqList, seqPeriod, seqOnTime, ExtGpio, chipViewer) #DON'T EDIT

    def catAdd(self, catName):
        if not catName in list(self.categoryDict.keys()):
            self.categoryDict[catName] = [] #initializes list for each category

    def seqAdd(self, seqCategory, seqName, seqDesc, seqList, seqPeriod, seqOnTime, ExtGpio, chipViewer):
        if threadElectrodeSeq == False:
            self.seq[seqName] = dummyThread(seqName)
        else:
            self.seq[seqName] = threadElectrodeSeq.ArduElecSeqThread(gpio=ExtGpio,
                                                        nameID=seqName,
                                                        Period=seqPeriod,
                                                        onTime=seqOnTime,
                                                        elecList= seqList
                                                        )
            self.seq[seqName].addViewer('UDP', chipViewer)
        self.seq[seqName].desc = seqDesc
        self.catAdd(seqCategory)
        self.categoryDict[seqCategory].append(seqName)

    def seqPrint(self, val=True):
        for seqName in list(self.seqDesc.keys()):
            print('%s -> %s'%(seqName, self.seqDesc[seqName]))

    def enOut(self, val=True):
        for seqName in list(self.seq.keys()):
            self.seq[seqName].enOut = val

    def stop(self):
        for seqName in list(self.seq.keys()):
            self.seq[seqName].stop()

    def startSeq(self, elecList, N=1, onTime=0.7, Period=1.0, moveSeq=False):
        freeSeq = False
        for seq in self.genSeq:
            if seq.enable == False:
                freeSeq = seq
        if freeSeq == False:
            seqName = 'genSeq%d'%(len(self.genSeq)+1)
            print('Building new genSeq %s'%(seqName))
            if moveSeq == True:
                self.genSeq.append(threadElectrodeSeq.MoveElecSeqThread(gpio=self.ExtGpio,
                                                                        nameID=seqName, #The name of the protocol
                                                                        Period=Period, #Total time [Sec]
                                                                        onTime=onTime, #On time for each electrod [Sec]
                                                                        elecList=elecList #The list itself
                                                                        )
                                   )
            else:
                self.genSeq.append(threadElectrodeSeq.ArduElecSeqThread(gpio=self.ExtGpio,
                                                                        nameID=seqName, #The name of the protocol
                                                                        Period=Period, #Total time [Sec]
                                                                        onTime=onTime, #On time for each electrod [Sec]
                                                                        elecList=elecList #The list itself
                                                                        )
                                   )

            freeSeq = self.genSeq[-1]
        else:
            print('Using %s'%(freeSeq.name))
            freeSeq.Period=Period #Total time [Sec]
            freeSeq.onTime=onTime #On time for each electrod [Sec]
            freeSeq.elecList=elecList #The list itself
        freeSeq.start(N)

    def ledTest(self, begin=1, end=104, dt=0.5):
        for led in range(begin, end):
            self.ExtGpio.pinPulse(led, dt)

    ####### SORTING SEQ ##############
    def sortseq(self,nr, t):
        '''Function defining a sorting electrode sequence.
        t = onTime
        nr = sequence number. See protocol file. '''
        self.seq['S%d'%(nr)].onTime = t
        self.seq['S%d'%(nr)].start(1)
        print(".....................")  

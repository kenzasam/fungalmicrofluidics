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

#Syringe pump modules
import sys
import os
import numpy
'''
qmixsdk_dir =  "C:/QmixSDK" #path to Qmix SDK
sys.path.append(qmixsdk_dir + "/lib/python")
os.environ['PATH'] += os.pathsep + qmixsdk_dir
from qmixsdk import qmixbus
from qmixsdk import qmixpump
from qmixsdk import qmixvalve
from qmixsdk.qmixbus import UnitPrefix, TimeUnit
'''

#####################

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

"""
Start of setup class
"""
class Setup():
    def __init__(self, ExtGpio, gpio, chipViewer, Pumps, Spec, PID):
        '''
        # >>>>>>> SETUP SPECIFIC PARAMETERS BLOCK <<<<<<< #
        deviceconfig="C:/QmixSDK/config/Nemesys_5units_20190308" #--> change path to device configuration folder
        syringe_param={'syringe_diam':[7.29,3.26,3.26,3.26,3.26],
                        'syringe_stroke':[59,40,40,40,40]} # --> change syringe parameters, in mm
        self.DropletVolume= 0.00025073 #-->  change to volume of 1 drop in microliter
        #>>>>>>>>>>>>> SETUP SPECIFIC PARAMETER BLOCK END  <<<<<<<<<<<<<
        '''

        self.init_pumps(Pumps=Pumps)
        self.init_spec(Spec=Spec)
        self.init_incubation(PID=PID)
        self.init_elecs(gpio=gpio,ExtGpio = ExtGpio, chipViewer = chipViewer)

    def init_spec(self, Spec):
        """
        Initializing spectrometer thread.
        """
        print '>>>  <<<'
        print '>>>  Checking spectrometer  <<<'
        if (Spec is None):
            print "Spectrometer thread not found! No spectrometer initiated. Spectomer thread is needed for this protocol."
            #sys.exit(1)
            #self.spec=Spec(Flame=Flame, Deviceconfig=deviceconfig)
        else:
            self.spec=Spec
            print "ok."

    def init_pumps(self, Pumps):
        """
        Initializing NeMESYS syringe pump thread.
        """
        print '>>>  <<<'
        print '>>>  Checking syringe pumps  <<<'
        #self.nem=Nem(Nemesys=Nemesys, Deviceconfig=deviceconfig, Syringe_param=syringe_param)
        if (Pumps is None):
            print "Pump bridge not found! No syringe pumps initiated. Syringe pumps are needed for this protocol."
        else:
            self.nem = Pumps
            print "ok."

    def init_incubation(self, PID):
        """
        Initializing PID thread.
        """
        print '>>>  <<<'
        print '>>>  Checking PID  <<<'

        if (PID is None):
            print "PID bridge not found! No incubation thread initiated. PID control is needed for this protocol."
            #sys.exit(1)
        else:
            self.PID = PID
            print "ok."

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
        b=[[37,38]]
        seqList = b # <-- Electrodes 1 and 2 actuated at same time. 3 actuated after 1 and 2.
        seqOnTime= 0.9 # <-- How long is the electrode actuated [Sec]
        seqPeriod= 1 # <-- Keep this at least 0.2 seconds above onTime [Sec]

        self.seqAdd(seqCategory, seqName, seqDesc, seqList, seqPeriod, seqOnTime, ExtGpio, chipViewer) #DON'T EDIT
        # /\ **  END OF SEQUENCE  ** /\
        # \/ ** START OF SEQUENCE ** \/
        seqCategory = 'Sorting'  #<-- EDIT THIS
        seqName = 'S2'  #<-- EDIT THIS
        seqDesc = ''  #<-- EDIT THIS
        b=[[42,78,41,100,40,75,39,97,38,72,94,37]]
        seqList = b # <-- Electrodes 1 and 2 actuated at same time. 3 actuated after 1 and 2.
        seqOnTime= 0.7 # <-- How long is the electrode actuated [Sec]
        seqPeriod= 1 # <-- Keep this at least 0.2 seconds above onTime [Sec]

        self.seqAdd(seqCategory, seqName, seqDesc, seqList, seqPeriod, seqOnTime, ExtGpio, chipViewer) #DON'T EDIT
        # /\ **  END OF SEQUENCE  ** /\
        # \/ ** START OF SEQUENCE ** \/
        seqCategory = 'Sorting'  #<-- EDIT THIS
        seqName = 'S3'  #<-- EDIT THIS
        seqDesc = ''  #<-- EDIT THIS
        b=[[42,78,41,100,40,75,39,97,38,72,94,37]]
        seqList = b # <-- Electrodes 1 and 2 actuated at same time. 3 actuated after 1 and 2.
        seqOnTime= 0.7 # <-- How long is the electrode actuated [Sec]
        seqPeriod= 1 # <-- Keep this at least 0.2 seconds above onTime [Sec]

        self.seqAdd(seqCategory, seqName, seqDesc, seqList, seqPeriod, seqOnTime, ExtGpio, chipViewer) #DON'T EDIT

    def catAdd(self, catName):
        if not catName in self.categoryDict.keys():
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
        for seqName in self.seqDesc.keys():
            print '%s -> %s'%(seqName, self.seqDesc[seqName])

    def enOut(self, val=True):
        for seqName in self.seq.keys():
            self.seq[seqName].enOut = val

    def stop(self):
        for seqName in self.seq.keys():
            self.seq[seqName].stop()

    def startSeq(self, elecList, N=1, onTime=0.7, Period=1.0, moveSeq=False):
        freeSeq = False
        for seq in self.genSeq:
            if seq.enable == False:
                freeSeq = seq
        if freeSeq == False:
            seqName = 'genSeq%d'%(len(self.genSeq)+1)
            print 'Building new genSeq %s'%(seqName)
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
            print 'Using %s'%(freeSeq.name)
            freeSeq.Period=Period #Total time [Sec]
            freeSeq.onTime=onTime #On time for each electrod [Sec]
            freeSeq.elecList=elecList #The list itself
        freeSeq.start(N)

    def ledTest(self, begin=1, end=104, dt=0.5):
        for led in range(begin, end):
            self.ExtGpio.pinPulse(led, dt)

    def pumpstartup(self,v=100):
        for i in range(5):
            self.nem.pump_calibration(self.nem.pumpID(i))
            self.nem.pump_aspirate(self.nem.pumpID(i), v)

    ####### droplet generation ###############
    def DropGen(self,n=1,t=0,pumpID=0):
        '''
        # n is amount of repeats (drops)
        # t is wait time (d*Period, seconds),
        # flrt is the flowrate
        # and pumpID is the pump from which dispensing happens
        if type(t)==float:
            print "time needs to be an integer"
            return
        print "making %d droplets" %(n)
        print "waiting %d seconds between droplets" %(t)
        #totalvolume=self.DropletVolume*n #calculate totalvolume loss
        #print "total volume loss [uL]: " ,totalvolume
        if self.DropletVolume < 0.0009: #self.dropletvolume you give as par on top
           DropletVolume=0.0008
           print "droplet volume is smaller than 0.001. "
        else:
           DropletVolume= self.DropletVolume
        #Calculate the flowrate by which aq flow needs to resuply 1 droplet
        #  this is the total volume of one drop
        #  devided by time in sec it takes to make 1 drop
        droptime = len(self.seq['DropGenL'].elecList) * self.seq['DropGenL'].Period # is an integer
        print 'time requiered to make 1 drop: %d sec' %(droptime)
        dropflowrate = DropletVolume / droptime #is a float
        if dropflowrate < 0.0006:
            dropflowrate=0.0006
        #Loop: (resupply one drop with Nem, Actuate and wait) x n times
        for i in range(n):
          self.nem.pump_dispense(self.nem.pumpID(pumpID), DropletVolume, dropflowrate) #dispense totalvolume
          print "resupplying w Nemesys done"
          DropGenLSeq = self.DropGenLSeq +[110]*t
          self.seq['DropGenL'].elecList = DropGenLSeq
          self.seq['DropGenL'].start(1)
          print "making drop %d" %(i+1)
          #while bt.BasicThread.isAlive()):
          time.sleep(droptime)
        print "....................."
        '''
    ####### droplet operations ##############
    def sort(self,nr):
        self.seq['S%d'%(nr)].start(1)
        print "....................."

    def incubation(self,RC=0.5,T=37,t=30):
    	self.PID.start()
        self.PID.RC_div_DT=RC
    	self.PID.ctrl(T)
        self.tempfeedbackstream(t,T,step=10)
    	#time.sleep(t)
        self.PID.stop()
        print "....................."

    def tempfeedbackstream(self,t, T, step=1):
        pad_str = ' ' * len('%d' % step)
        fbT= self.PID.getFeedback()
        for i in range(t, 0, -step):
            print 'Incubating at target %d C, currently %s\r C' % (T, fbT, pad_str),
            sys.stdout.flush()
            time.sleep(step)
            print 'Done incubating for %d sec at %d C!' % ( t, T)

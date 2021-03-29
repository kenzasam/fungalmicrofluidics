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

#from ArduBridge_ClR import SpecSP
from GSOF_ArduBridge import threadBasic as bt
import time, copy

#Syringe pump modules
import sys
import os
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
    def __init__(self, ExtGpio, gpio, chipViewer, Pumps, Spec, SpecSP, PID, ImgA):
        '''
        # >>>>>>> SETUP SPECIFIC PARAMETERS BLOCK <<<<<<< #
        deviceconfig="C:/QmixSDK/config/Nemesys_5units_20190308" #--> change path to device configuration folder
        syringe_param={'syringe_diam':[7.29,3.26,3.26,3.26,3.26],
                        'syringe_stroke':[59,40,40,40,40]} # --> change syringe parameters, in mm
        self.DropletVolume= 0.00025073 #-->  change to volume of 1 drop in microliter
        #>>>>>>>>>>>>> SETUP SPECIFIC PARAMETER BLOCK END  <<<<<<<<<<<<<
        '''

        self.init_pumps(Pumps=Pumps)
        self.init_spec(Spec=Spec, SpecSP=SpecSP)
        self.init_incubation(PID=PID)
        self.init_img_algo(imgA=ImgA)
        self.init_elecs(gpio=gpio,ExtGpio = ExtGpio, chipViewer = chipViewer)

    def init_spec(self, Spec, SpecSP):
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

        if (SpecSP is None):
            print "Spectrometer signal processing thread not found! No spectrometer initiated. Spectomer thread is needed for this protocol."
            #sys.exit(1)
            #self.spec=Spec(Flame=Flame, Deviceconfig=deviceconfig)
        else:
            self.specsp=SpecSP
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
            
    def init_img_algo(self, imgA):
        """
        Initializing imaging pipeline.
        """
        print '>>>  <<<'
        print '>>>  Checking imaging pipeline.  <<<'
        
        self.triggerpump = 0 #<-- Pump used for hardware trigger
        self.triggerflow = 0.01 #<-- flow in units as defined for pummps

        if (imgA is None):
            print "No imaging algorithm."
            #sys.exit(1)
        else:
            self.imgA = imgA
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
        b=[[]]
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
        '''startup function for pumps. Run to calibrate all pumps and aspirate v.
        v = volume to aspirate'''
        for i in range(5):
            self.nem.pump_calibration(self.nem.pumpID(i))
            self.nem.pump_aspirate(self.nem.pumpID(i), v)

    ####### SPECTROMETER #############
    def setInttime(self, t):
        '''Set the integration time of the FLAME spectrometer.
        t = time in msec'''
        try:
            self.spec.set_int_time(t)
            print ("Integration time set to %d ms") %(t)
        except:
            print("Error. Can't set integrtion time.")

    ####### SORTING ##############
    def sortseq(self,nr, t):
        '''Function defining a sorting electrode sequence.
        t = onTime
        nr = sequence number. See protocol file. '''
        self.seq['S%d'%(nr)].onTime = t
        self.seq['S%d'%(nr)].start(1)
        print "....................."
    
    def setGate(self, lowerI, upperI, lowerL, upperL):
        '''set lower intensity, upper intensity, 
        lower wavelength, upper wavelength'''
        try:
            self.specsp.gateI = [lowerI, upperI]
            print ("Gate set to %d - %d [RFU] ") %(lowerI, upperI)
            self.specsp.gateL = [lowerL,upperL]
            print ("Gate set to %d - %d [nm] ") %(lowerL, upperL)
        except:
            print("Error. Can't set gate.")

    def setDropTime(self,t):
        '''Set the droplet travel time (how long it takes for a droplet to travel from
         excitation point to sorting electrodes)
         t = time in sec'''
        try:
            self.specsp.t_wait = t
            print("Droplet travel time set to: %d sec ") %(t)
        except:
            print("Error. Can't set Droplet travel Time.")

    def setOnTime(self, t):
        '''Set the onTime for the pulsing electrode.
        t = time in sec.
        '''
        try:
            self.specsp.onTime = t
            print("onTime set to: %d sec ")%(t)
        except:
            print("Error. Can't set onTime.")

    def setElecs(self, pin_ct, pin_pulse):
        '''Set the electrode numbers for your sorting configuration.
        Set pin_ct = constant pin
        pin_pulse = pulsing sorting pin
        '''
        try:
            self.specsp.pin_ct = pin_ct
            self.specsp.pin_pulse = pin_pulse
            print("Pin_cte: %d , Pin_pulse: %d.") %(pin_ct, pin_pulse)
        except:
            print("Error. Can't set pint_cte or pin_pulse.")

    ####### PID ##############
    def incubation(self,RC=0.5,T=37,t=30):
        '''Function to start the PID process, set it to a certain temperature,
         and leave it running for a specific amount of time.
         Continuous printout of measured temperatures.
        '''
    	self.PID.start()
        self.PID.RC_div_DT=RC
    	self.PID.ctrl(T)
        self.tempfeedbackstream(t,T,step=10)
    	#time.sleep(t)
        self.PID.stop()
        print "....................."    

    def tempfeedbackstream(self,t, T, step=1):
        '''Continuous printout of measured temperatures.
        '''
        pad_str = ' ' * len('%d' % step)
        fbT= self.PID.getFeedback()
        for i in range(t, 0, -step):
            print 'Incubating at target %d C, currently %s\r C' % (T, fbT, pad_str),
            sys.stdout.flush()
            time.sleep(step)
            print 'Done incubating for %d sec at %d C!' % ( t, T)
    
    ##### IMAGING ALGO ######
    def ImgTrigger(self):
        '''Function to stop incubation, start pumps. Image aquisition based Hardware trigger.
        '''
        print('Trigger received from Imaging pipeline.')
        self.PID.stop()
        self.nem.pump_generate_flow(self.triggerpump, self.triggerflow)
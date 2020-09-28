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
## Protocol by Kenza Smalali
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
qmixsdk_dir =  "C:/QmixSDK" #path to Qmix SDK
sys.path.append(qmixsdk_dir + "/lib/python")
os.environ['PATH'] += os.pathsep + qmixsdk_dir
from qmixsdk import qmixbus
from qmixsdk import qmixpump
from qmixsdk import qmixvalve
from qmixsdk.qmixbus import UnitPrefix, TimeUnit


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
    def __init__(self, ExtGpio, gpio, chipViewer, Nemesys, Flame):
        # >>>>>>> PARAMETERS BLOCK <<<<<<< #
        deviceconfig="C:/QmixSDK/config/Nemesys_5units_20190308" #--> change path to device configuration folder
        syringe_param={'syringe_diam':[7.29,3.26,3.26,3.26,3.26],
                        'syringe_stroke':[59,40,40,40,40]} # --> change syringe parameters, in mm
        self.DropletVolume= 0.00025073 #-->  change to volume of 1 drop in microliter
        #>>>>>>>>>>>>> PARAMETER BLOCK END  <<<<<<<<<<<<<
        self.gpio = gpio
        self.ExtGpio = ExtGpio
        self.chipViewer = chipViewer
        self.seq = {} #initializes dictionary, which is an array of associations; returns associated value when a value is inputted
        self.categoryDict = {}
        print '>>>  <<<'
        print '>>>  Checking syringe pumps  <<<'
        self.nem=Nem(Nemesys=Nemesys, Deviceconfig=deviceconfig, Syringe_param=syringe_param)
        print '>>>  <<<'
        print '>>>  Checking spectrometer  <<<'
        self.spec=Spec(Flame=Flame, Deviceconfig=deviceconfig)
        ##############################################################
        ####\/\/\/ EXTRA USER FUNCTIONS \/\/\/#########################
        ###############################################################
        self.DropGenLSeq = [[61,84],[84,66],[66,90],[90,67],[61]]
        ##############################################################

        ##############################################################################
        ####\/\/\/ SEQUENCES \/\/\/###################################################
        """
        The Sorting function allows you to sort droplets to the bottom channel.
        """
        # \/ ** START OF SEQUENCE ** \/
        seqCategory = 'Sorting'  #<-- EDIT THIS
        seqName = 'S1'  #<-- EDIT THIS
        seqDesc = ''  #<-- EDIT THIS
        b=[[42,78,41,100,40,75,39,97,38,72,94,37]]
        seqList = b # <-- Electrodes 1 and 2 actuated at same time. 3 actuated after 1 and 2.
        seqOnTime= 0.7 # <-- How long is the electrode actuated [Sec]
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
        # /\ **  END OF SEQUENCE  ** /\
        ######################################################################################################################
        ######################################################################################################################

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
    def Sort(self,nr):
        self.seq['E%d'%(nr)].start(1)
        print "....................."

######################################################################################################################
######################################################################################################################
"""
End of Setup class
"""
"""
Start of Nem class
"""
class Nem():
    """
    This Nem class is used to define functions related to pump operation. In our case, we use a CETONI
    NeMYSES low pressure syringe pump setup with 5 modules.
    This code relies on an API provided by CETONI, by whom it is licensed.
    Inquiries:
    This code ibnterfaces with the API through ctypes.
    """
    """
    This class can be accessed in the IDLE by :
    >>> setup.nem.yourfunction()
    In case you need to provide a pump, make sure to access the pump object list, f.e.:
    >>> setup.nem.enable(setup.nem.pumpID(0))
    """
    def __init__(self, Nemesys, Deviceconfig, Syringe_param):
        self.deviceconfig=Deviceconfig
        self.syringe_diam=Syringe_param['syringe_diam']
        self.syringe_stroke=Syringe_param['syringe_stroke']
        if Nemesys==True:
            print '>>>  <<<'
            print '>>>  nemesys  <<<'
            print '>>> Starting Nemesys Bridge communication... <<<'
            self.bus= qmixbus.Bus()
            print 'Opening bus with deviceconfig', self.deviceconfig
            self.bus.open(self.deviceconfig, 0)
            pumpNameList = [] #pump handles assignment
            if pumpNameList == []:
                for id in range(5):
                    pumpNameList.append("neMESYS_Low_Pressure_%d_Pump"%(id+1))
            self.pumpsObjList=[] #make pump objects
            for pumpName in pumpNameList:
                pump=qmixpump.Pump()
                print '%s %s, obj.handle %s'%(pumpName, str(pump), str(pump.handle))
                pump.lookup_by_name(pumpName)
                print '%s %s, obj.handle %s'%(pumpName, str(pump), str(pump.handle))
                self.pumpsObjList.append(pump)
            print  '>>> Starting bus communication...<<<'
            self.bus.start()
            print '>>> Enabling and configuring SI units, syringe diameter and stroke for all pumps<<<'
            for i, pump in enumerate(self.pumpsObjList):
                print 'pump: %d'%(i)
                self.syringe_enable(pump)
                #print "Setting SI units..."
                self.syringe_units(pump)
                #print "Configuring syringe diameters..."
                self.syringe_config(pump, self.syringe_diam[i], self.syringe_stroke[i])
                pump.max_volume = pump.get_volume_max()
                print "max_volume = %f"%(pump.max_volume)
                pump.max_flow = pump.get_flow_rate_max()
                print "max_flow = %f"%(pump.max_flow)
            print '>>> done <<<'

        else:
            print '>>>  <<<'
            print '>>>  Nemesys is OFFLINE   <<<'

    def pumpID(self, pumpID):
        return self.pumpsObjList[pumpID]

    def syringe_enable(self, pump):
        print pump
        if pump.is_in_fault_state():
            pump.clear_fault()
            print 'error, pump fault %s'%(pump)
        if not pump.is_enabled():
            pump.enable(True)
            print 'pump %s enabled'%(pump)

    def syringe_config(self, pump, InnerDiam, stroke):
        print "Configuring syringe %s..." %(pump)
        pump.set_syringe_param(InnerDiam,stroke)
        print "Reading syringe config..."
        syringe = pump.get_syringe_param()
        print  "%s %.2f mm inner diameter" %(pump,syringe.inner_diameter_mm)
        print "%s %d mm max piston stroke" %(pump,syringe.max_piston_stroke_mm)

    def syringe_units(self, pump):
        print "Setting SI units %s ..." %(pump)
        pump.set_volume_unit(qmixpump.UnitPrefix.micro, qmixpump.VolumeUnit.litres)
        pump.set_flow_unit(qmixpump.UnitPrefix.micro, qmixpump.VolumeUnit.litres, qmixpump.TimeUnit.per_second)
        max_ul = pump.get_volume_max()
        print"Max. volume: ", max_ul
        max_ul_s = pump.get_flow_rate_max()
        print "Max. flow: ", max_ul_s

    def pump_generate_flow(self, pump, flow):
        print "Generating flow from %s ..." %(pump)
        pump.generate_flow(flow)
        time.sleep(1)
        flow_is = pump.get_flow_is()
        print 'flow is:', flow_is
        finished = self.wait_dosage_finished(pump, 2)
        if finished == True:
            print 'done'

    def pump_volume(self, pump, max_volume, max_flow):
        vlunit=pump.get_volume_unit()
        flunit=pump.get_flow_unit()
        print "Pumping %f %s at %f %s from %s ..."%(max_volume,vlunit, max_flow, flunit, pump)
        pump.pump_volume(max_volume, max_flow)
        finished = self.wait_dosage_finished(pump, 10)
        if finished == True:
            print 'done'

    def pump_dispense(self, pump, max_volume, max_flow ):
        vlunit=pump.get_volume_unit()
        flunit=pump.get_flow_unit()
        print "Dispensing %f %s at %f %s from %s ..."%(max_volume,vlunit, max_flow, flunit, pump)
        pump.dispense(max_volume, max_flow)
        finished = self.wait_dosage_finished(pump, 2)
        if finished == True:
            print 'done'

    def pump_aspirate(self, pump, max_volume):
        print("Testing aspiration...")
        pump.aspirate(max_volume, pump.max_flow)
        finished = self.wait_dosage_finished(pump, 30)
        if finished == True:
            print 'done'

    def pump_stop(self, pump):
        pump.stop_pumping()
        print'stopped pump %s ' %(pump)

    def pump_stop_all(self):
        for pump in self.pumpsObjList:
          self.pump_stop(pump)
        print'stopped all pumps'

    def wait_dosage_finished(self, pump, timeout_seconds): #static method
        #The function waits until the last dosage command has finished
        #until the timeout occurs.
        timer = qmixbus.PollingTimer(timeout_seconds * 1000)
        message_timer = qmixbus.PollingTimer(500)
        result = True
        while (result == True) and not timer.is_expired():
            time.sleep(0.1)
            if message_timer.is_expired():
                print "Fill level: ", pump.get_fill_level()
                message_timer.restart()
            result = pump.is_pumping()
        return not result

    def wait_calibration_finished(self,pump, timeout_seconds): #static method
        #The function waits until the given pump has finished calibration or
        #until the timeout occurs.
        timer = qmixbus.PollingTimer(timeout_seconds * 1000)
        result = False
        while (result == False) and not timer.is_expired():
            time.sleep(0.1)
            result = pump.is_calibration_finished()
        return result

    def pump_calibration(self, pump):
        print "Calibrating pump..."
        pump.calibrate()
        time.sleep(0.2)
        calibration_finished = self.wait_calibration_finished(pump, 30)
        print "Pump calibrated: ", calibration_finished

"""
Start of spectrometer class
"""
class Spec():
    def __init__(self, Flame, Deviceconfig):

        self.Deviceconfig=Deviceconfig
        if Flame == True:
            print '>>>  <<<'
            print '>>>  FLAME is online <<<'
            print '>>> Starting Flame Bridge communication... <<<'


        else:
            print '>>>  <<<'
            print '>>>  FLAME is OFFLINE   <<<'

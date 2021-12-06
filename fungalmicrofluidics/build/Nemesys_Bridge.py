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
June 2020: V1.0
March 2021 v1.1
"""

import time
import sys
import os
qmixsdk_dir =  "C:/QmixSDK" #path to Qmix SDK
sys.path.append(qmixsdk_dir + "/lib/python")
os.environ['PATH'] += os.pathsep + qmixsdk_dir
from qmixsdk import qmixbus
from qmixsdk import qmixpump
from qmixsdk import qmixvalve
from qmixsdk.qmixbus import UnitPrefix, TimeUnit


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
    def __init__(self, deviceconfig, syringe_diam, syringe_stroke):
        self.deviceconfig=deviceconfig
        self.DropletVolume= 0.00025073 #-->  change to volume of 1 drop in microliter
        self.syringe_diam=syringe_diam
        self.syringe_stroke=syringe_stroke

        print('>>>  <<<')
        print('>>>  nemesys  <<<')
        print('>>> Starting Nemesys Bridge communication... <<<')
        self.bus= qmixbus.Bus()
        print('Opening bus with deviceconfig', self.deviceconfig)
        self.bus.open(self.deviceconfig, 0)
        pumpNameList = [] #pump handles assignment
        if pumpNameList == []:
            for id in range(5):
                pumpNameList.append("neMESYS_Low_Pressure_%d_Pump"%(id+1))
        self.pumpsObjList=[] #make pump objects
        for pumpName in pumpNameList:
            pump=qmixpump.Pump()
            print('{} {}, obj.handle {}'.format(pumpName, str(pump), str(pump.handle)))
            pump.lookup_by_name(pumpName)
            print('{} {}, obj.handle {}'.format(pumpName, str(pump), str(pump.handle)))
            self.pumpsObjList.append(pump)
        print('>>> Starting bus communication...<<<')
        try:
            self.bus.start()
            pumpfail=False
            print("Bus started.... ")
        except:
            print("Can't start bus. Skipping pump setup. Do NOT use pumps! .... ")
            pumpfail=True
        if pumpfail!=True:
            print('>>> Enabling and configuring SI units, syringe diameter and stroke for all pumps<<<')
            for i, pump in enumerate(self.pumpsObjList):
                print('pump:'+i)
                self.syringe_enable(pump)
                self.syringe_units(pump)
                self.syringe_config(pump, self.syringe_diam[i], self.syringe_stroke[i])
                pump.max_volume = pump.get_volume_max()
                print("max_volume ={}".format(pump.max_volume))
                pump.max_flow = pump.get_flow_rate_max()
                print("max_flow = {}".format(pump.max_flow))
            print('>>> done <<<')

    def pumpID(self, pumpID):
        return self.pumpsObjList[pumpID]

    def syringe_enable(self, pump):
        print(pump)
        if pump.is_in_fault_state():
            pump.clear_fault()
            print('error, pump fault '+pump)
        if not pump.is_enabled():
            pump.enable(True)
            print('pump {} enabled'.format(pump))

    def syringe_config(self, pump, InnerDiam, stroke):
        print("Configuring syringe {}..." .format(pump))
        pump.set_syringe_param(InnerDiam,stroke)
        print("Reading syringe config...")
        syringe = pump.get_syringe_param()
        print("{} {} mm inner diameter" .format(pump,syringe.inner_diameter_mm))
        print("{} {} mm max piston stroke".format(pump,syringe.max_piston_stroke_mm))

    def syringe_units(self, pump):
        print("Setting SI units {} ..." .format(pump))
        pump.set_volume_unit(qmixpump.UnitPrefix.micro, qmixpump.VolumeUnit.litres)
        pump.set_flow_unit(qmixpump.UnitPrefix.micro, qmixpump.VolumeUnit.litres, qmixpump.TimeUnit.per_second)
        max_ul = pump.get_volume_max()
        print("Max. volume: ", max_ul)
        max_ul_s = pump.get_flow_rate_max()
        print("Max. flow: ", max_ul_s)

    def pump_generate_flow(self, pump, flow):
        print("Generating flow from {} ..." .format(pump))
        pump.generate_flow(flow)
        time.sleep(1)
        flow_is = pump.get_flow_is()
        print('flow is:', flow_is)
        finished = self.wait_dosage_finished(pump, 2)
        if finished == True:
            print('done')

    def pump_volume(self, pump, max_volume, max_flow):
        vlunit=pump.get_volume_unit()
        flunit=pump.get_flow_unit()
        print("Pumping {} {} at {} {} from {} ...".format(max_volume,vlunit, max_flow, flunit, pump))
        pump.pump_volume(max_volume, max_flow)
        finished = self.wait_dosage_finished(pump, 10)
        if finished == True:
            print('done')

    def pump_dispense(self, pump, max_volume, max_flow ):
        vlunit=pump.get_volume_unit()
        flunit=pump.get_flow_unit()
        print("Dispensing {} {} at {} {} from {} ...".format(max_volume,vlunit, max_flow, flunit, pump))
        pump.dispense(max_volume, max_flow)
        finished = self.wait_dosage_finished(pump, 2)
        if finished == True:
            print('done')

    def pump_aspirate(self, pump, max_volume):
        print("Testing aspiration...")
        pump.aspirate(max_volume, pump.max_flow)
        finished = self.wait_dosage_finished(pump, 30)
        if finished == True:
            print('done')

    def pump_stop(self, pump):
        pump.stop_pumping()
        print('stopped pump ' +pump)

    def pump_stop_all(self):
        for pump in self.pumpsObjList:
          self.pump_stop(pump)
        print('stopped all pumps')

    def wait_dosage_finished(self, pump, timeout_seconds): #static method
        '''The function waits until the last dosage command has finished
        until the timeout occurs.'''
        timer = qmixbus.PollingTimer(timeout_seconds * 1000)
        message_timer = qmixbus.PollingTimer(500)
        result = True
        while (result == True) and not timer.is_expired():
            time.sleep(0.1)
            if message_timer.is_expired():
                print("Fill level: ", pump.get_fill_level())
                message_timer.restart()
            result = pump.is_pumping()
        return not result

    def wait_calibration_finished(self,pump, timeout_seconds): #static method
        '''The function waits until the given pump has finished calibration or
        until the timeout occurs.'''
        timer = qmixbus.PollingTimer(timeout_seconds * 1000)
        result = False
        while (result == False) and not timer.is_expired():
            time.sleep(0.1)
            result = pump.is_calibration_finished()
        return result

    def pump_calibration(self, pump):
        print("Calibrating pump...")
        pump.calibrate()
        time.sleep(0.2)
        calibration_finished = self.wait_calibration_finished(pump, 30)
<<<<<<< HEAD:fungalmicrofluidics/build/Nemesys_Bridge.py
        print("Pump calibrated: ", calibration_finished)
=======
        print "Pump calibrated: ", calibration_finished
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e:fungalmicrofluidics/Nemesys_Bridge.py

    def pumpstartup(self,v=100):
        '''startup function for pumps. Run to calibrate all pumps and aspirate v.
        v = volume to aspirate'''
        for i in range(5):
            self.pump_calibration(self.nem.pumpID(i))
            self.pump_aspirate(self.nem.pumpID(i), v)

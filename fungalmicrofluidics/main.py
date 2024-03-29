"""
Copyright, 2020, Guy  Soffer, Kenza Samlali
"""

"""
This file is part of fungalmicrofluidics.

    fungalmicrofluidics is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    fungalmicrofluidics is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with fungalmicrofluidics.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
Script to build an ArduBridge environment
To customize the environment to your needs: You will need to change
the parameters in the "PARAMETER BLOCK" in the __main__ section.
Also, if PID/PUMPS/SPEC are set to True, please see
repective instances to modify appropriate variables.
"""
#Basic modules to load
import time
import os, sys
import importlib
from GSOF_ArduBridge import udpControl
from GSOF_ArduBridge import ArduBridge
from GSOF_ArduBridge import ElectrodeGpioStack
from GSOF_ArduBridge import UDP_Send
<<<<<<< HEAD
from build import Nemesys_Bridge as Nemesys_Bridge
from build import  TCP_Send as TCP_Send
from build import threadSpec as threadSpec
=======
import build.Nemesys_Bridge as Nemesys_Bridge
import build.TCP_Send as TCP_Send
import build.threadSpec as threadSpec
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e

def extEval(s):
    '''
    A function for udpControl (client), that evaluates the reveived package.
    eval() reads the string, compiles it and returns its value
    '''
    s=str(s)
    eval(s)

def close():
    if udpConsol != False:
        udpConsol.active = False
    if SETUP != False:
        if PUMPS != False:
            setup.nem.bus.stop()
<<<<<<< HEAD
            print('Nemesys Bus closed...\n')
        if SPEC != False and Spec.SPECstatus != False:
            setup.spec.stop()
            print('Spec thread stoped...\n')
        if SPECSP != False:
            setup.specsp.stop()
            print('Spec thread stoped...\n')
        setup.stop()
    ardu.OpenClosePort(0)
    print('Bye Bye...')
=======
            print 'Nemesys Bus closed...\n'
        if SPEC != False and Spec.SPECstatus != False:
            setup.spec.stop()
            print 'Spec thread stoped...\n'
        if SPECSP != False:
            setup.specsp.stop()
            print 'Spec thread stoped...\n'
        setup.stop()
    ardu.OpenClosePort(0)
    print 'Bye Bye...'
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e
    
def getProgramFolder():
        moduleFile = __file__
        moduleDir = os.path.split(os.path.abspath(moduleFile))[0]
        programFolder = os.path.abspath(moduleDir)
        return programFolder

configPath = os.path.join(getProgramFolder(), "user_config")

if __name__ == "__main__":
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/##################################################
    ########################################################################################
<<<<<<< HEAD
    user= 'user name'
    lib = 'protocol_name' #<--CHANGE PROTOCOL file name
=======
    user= 'Kenza Samlali'
    lib = 'protocol_KS_clr_sort_nem5_v2' #<--CHANGE PROTOCOL file name
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e
    port = 'COM20' #'/dev/cu.usbmodem14201' #'COM20' <--Change to the correct COM-Port to access the Arduino
    baudRate = 115200 *2 #<--ArduBridge_V1.0 uses 115200 other versions use 230400 = 115200*2
    ONLINE = True #<--True to enable work with real Arduino, False for simulation only.
    ELEC_EN = True #<-- False for simulation
    PUMPS = False #<-- True when user wants to use Nemesys pump through python.
    SPEC = True #<-- True when user wants to use a spectrometer thread.
    SPECSP = True #<-- True when user wants to perform signal processing on spectrum .
    STACK_BUILD = [0x40,0x41,0x42,0x43,0x44,0x45] #<-- Adresses for port expanders on optocoupler stack
    PORT_BASE = 7000
    REMOTE_CTRL_PORT = PORT_BASE + 10 #Client, ArduBridge on port 7010
    #/\/\/\   PARAMETERS BLOCK END  /\/\/\################################################
    ######################################################################################
    '''
    import user protocol
    '''
<<<<<<< HEAD
=======
    #protocol = __import__(lib)
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e
    protocol = importlib.import_module("user_config."+lib)
    SETUP=False
    '''
    Setting up Server and Clients (UDP and TCP networking protocols)
    '''
    udpSendChip = UDP_Send.udpSend(nameID='UDP2', DesIP='127.0.0.1', DesPort=PORT_BASE +1)
    tcpSendSpec = TCP_Send.tcpSend(nameID='TCP1', DesIP='127.0.0.1', DesPort=PORT_BASE +2)
    udpConsol = False
    if REMOTE_CTRL_PORT > 1:
        udpConsol = udpControl.udpControl(nameID='udpIDLE', RxPort=REMOTE_CTRL_PORT, callFunc=extEval)
<<<<<<< HEAD
        print('Remote-Consol-Active on port %s\n'%(str(REMOTE_CTRL_PORT)))
    '''
    Starting communications with electrode stack and Arduino
    '''
    print('Using port %s at %d'%(port, baudRate))
    ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate )
    if ONLINE:
        ardu.OpenClosePort(1)
        print('Connecting to Arduino ON-LINE.')
    else:
        print('Arduino OFF-LINE. Simulation mode')
=======
        print 'Remote-Consol-Active on port %s\n'%(str(REMOTE_CTRL_PORT))
    '''
    Starting communications with electrode stack and Arduino
    '''
    print 'Using port %s at %d'%(port, baudRate)
    ardu = ArduBridge.ArduBridge( COM=port, baud=baudRate )
    if ONLINE:
        ardu.OpenClosePort(1)
        print 'Connecting to Arduino ON-LINE.'
    else:
        print 'Arduino OFF-LINE. Simulation mode'
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e
    ardu.GetID()
    ExtGpio = ElectrodeGpioStack.ExtGpioStack(i2c=ardu.i2c, devList=STACK_BUILD, v=False)#True)
    ExtGpio.init()
    ExtGpio.init()
    ardu.Reset()
<<<<<<< HEAD
    print('Stack and Ardu ready...\n')
=======
    print 'Stack and Ardu ready...\n'
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e
    
    '''
    Setting up spectrometer thread and server.
    This will allow you to retrieve data from a spectrometer and plot it.
    '''
<<<<<<< HEAD
    print('Spectrometer Thread status: %s' %(SPEC))
=======
    print 'Spectrometer Thread status: %s' %(SPEC)
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e
    if SPEC == True:
        #\/\/\/ CHANGE THESE PARAMETERS \/\/\/##################################################
        ########################################################################################
        #threadSpec = __import__('threadSpec') # delete when you place in ArduBridge. For now place thread in folder
        Spec = threadSpec.Flame(nameID ='FLAME',    #<-- Thread proces name
                                device = 'FLMS04421',#<-- Spectrometer serial number FLMS04421. If empty, first available.
                                autorepeat = True,  #<-- Auto repeat measurements
                                autosave = False,   #<-- Enable Auto Save
                                dark_frames = 1,    #<-- The nr of dark frames
                                enable_plot = True, #<-- Enable plotting
                                output_file ='Snapshot.dat', #<-- File format for saved data.
                                scan_frames = 1,    #<-- Number of frames averaged after which measurement resets.
                                scan_time = 50000 #<-- Integration time in microseconds
                                )
        #/\/\/\   PARAMETERS BLOCK END  /\/\/\################################################
        ######################################################################################
        specViewer=tcpSendSpec
        Spec.addViewer('TCPspec',specViewer)
<<<<<<< HEAD
        print('Type Spec.start() to start the spectrometer thread process\n')
=======
        print 'Type Spec.start() to start the spectrometer thread process\n'
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e
    else:
        Spec = None

    '''
    Use spectrometer signal processing library. 
    This will allow you to analyze the spectrum from SPEC.
    A sorting thread autonomously sorts droplets above a treshold.
    '''
<<<<<<< HEAD
    print('Spectrometer Signal Processing status: %s' %(SPECSP))
    if SPEC and SPECSP == True:
=======
    print 'Spectrometer Signal Processing status: %s' %(SPECSP)
    if SPEC and SPECSP == True:
    #if SPECSP == True:
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e
        #\/\/\/ CHANGE THESE PARAMETERS \/\/\/##################################################
        ########################################################################################
        SpecSP = threadSpec.Processing (gpio =  ExtGpio,
                                        Period = 0.1 ,          #<-- Period-time of the control-loop [s]. 1 runs it once. Defines plotting speed.
                                        nameID = 'Auto Sort',
                                        intensity_gate = [500, 10000],   #<-- Gating peak intensity [RFU]: range for which trigger goes.
                                        wavelength_gate = [510,550],  #<-- [min,max] wavelength of the peak(s) in [nm]
                                        pkcount = 0,          #<-- number of events to record. 0 or False for infinite
                                        noise = 500,           #<-- background noise level.
                                        DenoiseType = 'BW',     #<-- BW, Butterworth filter
                                        PeakProminence = None, #
                                        PeakWlen = None, #
                                        PeakThreshold = None,     #100, # Vertical distance to neighbouring peaks
                                        PeakWidth = [15,200],    #<-- [min,max] width of the peak(s) in [nm]
                                        AutoSave = True,        #<-- Enable Auto-saving of Peak info during auto-sort
                                        output_file = 'PeakData.dat' , #<-- File format for saved data.
                                        Elec = True,           #<-- Enable electrodes
                                        Pin_cte = 75, #37,       #<-- electrode nr to turn on constantly
                                        Pin_pulse = 98, #38,     #<-- electrode nr to pulse for sorting
                                        Pin_onTime = 0.3,   #<-- pulse on time [sec].
                                        t_wait=0.1          #<-- time between detection and electrode pulse [sec]
                                        )
        #/\/\/\   PARAMETERS BLOCK END  /\/\/\################################################
        ######################################################################################                                
        SpecSP.enIO(True) # sets Spec.enOut to True
        Spec.SPS = SpecSP # self.SPS Instance in threadSpec.Flame class
        SpecSP.spec = Spec
<<<<<<< HEAD
        print('Access Spec signal processing by typing "SpecSP.". Change sorting Gate and peakfinding properties accordingly before starting Auto-Sort.')
        print('Type "SpecSP.start() to start the auto-sort process."')
=======
        print 'Access Spec signal processing by typing "SpecSP.". Change sorting Gate and peakfinding properties accordingly before starting Auto-Sort.'
        print 'Type "SpecSP.start() to start the auto-sort process."'
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e
    else:
        SpecSP = None

    '''
    Setting up Nemesys syringe pump bridge.
    '''
<<<<<<< HEAD
    print('Pumps status: %s' %(PUMPS))
=======
    print 'Pumps status: %s' %(PUMPS)
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e
    if PUMPS == True:
        #\/\/\/ CHANGE THESE PARAMETERS \/\/\/##################################################
        ########################################################################################
        #Pumpsbridge= __import__('Nemesys_Bridge')  #<-- change protocol file if needed
        Pumps = Nemesys_Bridge.Nem( deviceconfig="C:/QmixSDK/config/Nemesys_5units_20190308", #<-- change path to device configuration folder
                                syringe_diam=[7.29,3.26,3.26,3.26,3.26], #<-- syringe diameter, in mm
                                syringe_stroke=[59,40,40,40,40] #<-- syringe stroke length, in mm
                                )
        #/\/\/\   PARAMETERS BLOCK END  /\/\/\################################################
        ######################################################################################
<<<<<<< HEAD
        print('Syringe pumps ready...')
=======
        #nem=nemesysprot.nemesys(cfg=deviceconfig)
        print 'Syringe pumps ready...'
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e
    else:
        Pumps = None

    '''
    Start printouts
    '''
<<<<<<< HEAD
    print(("/\  "*10))
    print(("  \/"*10))
    print('Now: %s'%(time.strftime("%Y-%m-%d %H:%M")))
    print('')
    print('USER: %s'%(user))
    print('ASSIGNED PROTOCOL: using %s'%(lib))
    print('')
    print('The protocol you are using, requires the NeMESYS syringe pump add-on')
    print('Change the device config file if needed')
    print('Change the NeMESYS to True or False to go online')
    print('status: %s' %(PUMPS))
    print('Change the SPEC spectrometer to True or False to go online')
    print('status: %s' %(SPEC))
    print('Loading protocol: %s' %(lib))
=======
    print("/\  "*10)
    print("  \/"*10)
    print 'Now: %s'%(time.strftime("%Y-%m-%d %H:%M"))
    print ''
    print 'USER: %s'%(user)
    print 'ASSIGNED PROTOCOL: using %s'%(lib)
    print ''
    if (lib =='protocol_KS_clr_sort_nem5_v2') :
      print 'The protocol you are using, requires the NeMESYS syringe pump add-on'
      print 'Change the device config file if needed'
      print 'Change the NeMESYS to True or False to go online'
      print 'status: %s' %(PUMPS)
      print 'Change the SPEC spectrometer to True or False to go online'
      print 'status: %s' %(SPEC)
    print 'Loading protocol: %s' %(lib)
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e
    ###############
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/#
    ''' If adding new methods to the setup class, please ammend here for correct class instance.
    '''
    setup = protocol.Setup(ExtGpio=ExtGpio, gpio=ardu.gpio, chipViewer=udpSendChip.Send, Pumps=Pumps, Spec=Spec, SpecSP=SpecSP)
    ##
    ###############
    SETUP = True
    setup.enOut(ELEC_EN)
    prot = protocol.Protocol(setup)
<<<<<<< HEAD
    print('')
    print(("/\  "*10))
    print(("  \/"*10))
=======
    print ''
    print("/\  "*10)
    print("  \/"*10)
>>>>>>> f69241a8f1f1f172398eece622e0d31d1521301e

    if raw_input('Run GUI? [y/n]') == 'y':
        os.system('python GUI_fungalsorting.py')
    #########################

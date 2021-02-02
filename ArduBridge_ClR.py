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
    along with GSOF_ArduBridge.  If not, see <https://www.gnu.org/licenses/>.
"""

"""
Script to build an ArduBridge environment
To customize the environment to your needs: You will need to change
the parameters in the "PARAMETER BLOCK" in the __main__ section.
Also, if PID/PUMPS/SPEC are set to True, please see
repective instances to modify appropriate variables.
"""
########## RUN ANY GUI, AFTER RUNNING THIS FILE ##########
#Basic modules to load
import time
import sys
from GSOF_ArduBridge import udpControl
from GSOF_ArduBridge import ArduBridge
from GSOF_ArduBridge import ElectrodeGpioStack
from GSOF_ArduBridge import threadPID
from GSOF_ArduBridge import UDP_Send
import Nemesys_Bridge
import TCP_Send
import threadPID_KS
import threadSpec
#from GSOF_ArduBridge import threadFLAME
##qmixsdk_dir = "C:/QmixSDK" #path to Qmix SDK
#sys.path.append(qmixsdk_dir + "/lib/python")
#os.environ['PATH'] += os.pathsep + qmixsdk_dir

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
            print 'Nemesys Bus closed...'
        if PID != False & Pid.PIDstatus != False:
            PID.stop()
            print 'PID thread stopped...'
        if SPEC != False & Spec.SPECstatus != False:
            Spec.stop()
            print 'Spec thread stopped...'
        setup.stop()
    ardu.OpenClosePort(0)
    print 'Bye Bye...'

if __name__ == "__main__":
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/##################################################
    ########################################################################################
    user= 'Kenza Samlali'
    lib = 'protocol_KS_clr_sort_nem5_v2' #<--CHANGE PROTOCOL file name
    port = 'COM20' #'/dev/cu.usbmodem14201' #'COM20' <--Change to the correct COM-Port to access the Arduino
    baudRate = 115200 *2 #<--ArduBridge_V1.0 uses 115200 other versions use 230400 = 115200*2
    ONLINE = True #<--True to enable work with real Arduino, False for simulation only.
    ELEC_EN = True #<-- False for simulation
    PID = True #<-- True / False to build a PID controller.
    PUMPS = False #<-- True when user wants to use Nemesys pump through python.
    SPEC = True #<-- True when user wants to use a spectrometer thread.
    SPECSP = True #<-- True when user wants to perform signal processing on spectrum .
    GUI = False #<-- True for running GUI through serial
    STACK_BUILD = [0x40,0x41,0x42,0x43,0x44,0x45] #<-- Adresses for port expanders on optocoupler stack
    PORT_BASE = 7000
    REMOTE_CTRL_PORT = PORT_BASE + 10 #Client, ArduBridge on port 7010
    #/\/\/\   PARAMETERS BLOCK END  /\/\/\################################################
    ######################################################################################
    '''
    import user protocol
    '''
    protocol = __import__(lib)
    SETUP=False
    '''
    Setting up Server and Clients
    '''
    udpSendPid = UDP_Send.udpSend(nameID='UDP1', DesIP='127.0.0.1', DesPort=PORT_BASE +0)
    udpSendChip = UDP_Send.udpSend(nameID='UDP2', DesIP='127.0.0.1', DesPort=PORT_BASE +1)
    tcpSendSpec = TCP_Send.tcpSend(nameID='TCP1', DesIP='127.0.0.1', DesPort=PORT_BASE +2)
    udpConsol = False
    if REMOTE_CTRL_PORT > 1:
        udpConsol = udpControl.udpControl(nameID='udpIDLE', RxPort=REMOTE_CTRL_PORT, callFunc=extEval)
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
    ardu.GetID()
    ExtGpio = ElectrodeGpioStack.ExtGpioStack(i2c=ardu.i2c, devList=STACK_BUILD, v=False)#True)
    ExtGpio.init()
    ExtGpio.init()
    ardu.Reset()
    print 'Stack and Ardu ready...\n'
    '''
    Setting up PID thread and server
    '''
    print 'PID status: %s' %(PID)
    if PID == True:
        ### ###
        Pid = threadPID_KS.ArduPidThread(bridge=ardu,
                                      nameID='PID', #proces name
                                      Period=0.5,   #Period-time of the control-loop. PID calculation cycle time in sec.
                                      fbPin=1,      #The analog pin (Ardu) of the temp sensor.
                                      outPin=10,    #The output pin  of the driver (Ardu connection).
                                      dirPin=7      #The direction pin for the driver (Ardu connection).
                                      )
        Pid.PID.Kp = 30 # proportional control of PID
        Pid.PID.Ki = 1.2 # integral of PID
        Pid.PID.Kd = 0.0 # rate of change of PID (derivative)
        Pid.RC_div_DT = 10.0 # time constant, determining how fast you reach settle point
        ### ^^^ ^^^ ^^^ ###
        pidViewer=udpSendPid.Send
        Pid.addViewer('UDPpid',pidViewer) #'UDP',udpSendPid1.Send)
        Pid.enIO(True) #PID.enOut = True
        ardu.gpio.pinMode(7,0) # Initialize pin to 0
        print 'type PID.start() to start the PID thread process\n'
        #moclo = thermalCycle.thermoCycler(pid=PID,pntList=tempList)
    '''
    Setting up spectrometer thread and server
    '''
    print 'Spectrometer Thread status: %s' %(SPEC)
    if SPEC == True:
        #threadSpec = __import__('threadSpec') # delete when you place in ArduBridge. For now place thread in folder
        Spec = threadSpec.Flame(nameID ='FLAME', # Thread proces name
                                Period = 0, # Period-time of the control-loop. Defines plotting speed.
                                device = 'FLMS04421', # Spectrometer serial number FLMS04421. If empty, first available.
                                autorepeat = True, # Auto repeat measurements
                                autosave = False, # Enable Auto Save
                                dark_frames = 1, # The nr of dark frames
                                enable_plot = True, # Enable plotting
                                output_file ='Snapshot-%Y-%m-%dT%H:%M:%S%z.dat',
                                scan_frames = 1, # Number of frames averaged after which measurement resets.
                                scan_time = 100000, # Integration time in microseconds
                                )
        specViewer=tcpSendSpec
        Spec.addViewer('TCPspec',specViewer)
        print 'Type Spec.start() to start the spectrometer thread process\n'
    else:
        Spec = None

    '''
    Use spectrometer signal processing library
    '''
    print 'Spectrometer Signal Processing status: %s' %(SPECSP)
    if SPEC and SPECSP == True:
        SpecSP = threadSpec.Processing (treshold = 8000, # Treshold peak intensity above which trigger goes.
                                        PeakProminence = None,
                                        PeakWidth = None,
                                        PeakWlen = None, 
                                        DenoiseType = 'BW') # BW, Buterworth filter
        Spec.SPS = SpecSP # self.SPS Instance in threadSpec.Flame class

        print 'Spectrometer signal processing library initiated. Access by typing "SpecSP."'
    else:
        SpecSP = None

    '''
    Setting up Nemesys syringe pump bridge
    '''
    print 'Pumps status: %s' %(PUMPS)
    if PUMPS == True:
        #Pumpsbridge= __import__('Nemesys_Bridge')  #--> change protocol file if needed
        Pumps = Pumpsbridge.Nem(
                deviceconfig="C:/QmixSDK/config/Nemesys_5units_20190308", #change path to device configuration folder
                syringe_diam=[7.29,3.26,3.26,3.26,3.26], #syringe diameter, in mm
                syringe_stroke=[59,40,40,40,40] #syringe stroke length, in mm
                )
        #nem=nemesysprot.nemesys(cfg=deviceconfig)
        print 'Syringe pumps ready...'
    else:
        Pumps = None

    '''
    Start printouts
    '''
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
    setup = protocol.Setup(ExtGpio=ExtGpio, gpio=ardu.gpio, chipViewer=udpSendChip.Send, Pumps=Pumps, Spec=Spec, PID=PID)

    #SETUP= False
    #print 'setup wrongsihsoihs'

    SETUP = True
    setup.enOut(ELEC_EN)
    prot = protocol.Protocol(setup)
    #setup = protocol.Setup(ExtGpio=ExtGpio, gpio=ardu.gpio, chipViewer=udpSendChip.Send, Pumps=Pumps)
    print ''
    if GUI == True:
          gui=__import__('GUI_KS_Nemesys.GUI_KS_SC_nemesys')
          print 'Start ChipViewer to control droplet movement.'
    '''
    else:
      setup = protocol.Setup(ExtGpio=ExtGpio, gpio=ardu.gpio, chipViewer=udpSendChip.Send)
    '''
    print("/\  "*10)
    print("  \/"*10)
    #########################

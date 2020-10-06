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
To customize the environment to your needs. You will need to change
he parameters in the "PARAMETER BLOCK" in the __main__ section
"""
########## RUN CHIPVIEWER AND LLGUI AFTER RUNNING THIS FILE ##########
#Basic modules to load
import time
from GSOF_ArduBridge import udpControl
from GSOF_ArduBridge import ArduBridge
from GSOF_ArduBridge import ElectrodeGpioStack
from GSOF_ArduBridge import threadPID

#from GSOF_ArduBridge import threadPID_KS as threadPID
from GSOF_ArduBridge import UDP_Send
#from GSOF_ArduBridge import threadFLAME
##qmixsdk_dir = "C:/QmixSDK" #path to Qmix SDK
#sys.path.append(qmixsdk_dir + "/lib/python")
#os.environ['PATH'] += os.pathsep + qmixsdk_dir

def extEval(s):
    s=str(s)
    eval(s)

def close():
    if PUMPS != False:
       setup.nem.bus.stop()
       print 'Nemesys Bus closed...'

    if udpConsol != False:
        udpConsol.active = False
    setup.stop()
    ardu.OpenClosePort(0)
    print 'Bye Bye...'

def tempTC1047(pin=0, vcc=5.0):
    b = ardu.an.analogRead(pin)
    v = b*vcc/1024.0
    T = 100*(v -0.5)

if __name__ == "__main__":
    #\/\/\/ CHANGE THESE PARAMETERS \/\/\/##################################################
    ########################################################################################
    user= 'Kenza Samlali'
    lib = 'protocol_KS_clr_sort_nem5_v2' #<--CHANGE PROTOCOL file name
    port = 'COM20' #COM20 #/dev/cu.usbmodem14201 <--Change to the correct COM-Port to access the Arduino
    baudRate = 115200 *2 #<--ArduBridge_V1.0 uses 115200 other versions use 230400 = 115200*2
    ONLINE = True #<--True to enable work with real Arduino, False for simulation only.
    ELEC_EN = True #<-- False for simulation
    PID1 = False #<-- True / False to build a PID controller.
    PUMPS= False #<-- True when user wants to use Nemesys pump through python.
    SPECGUI = False #<-- True when user wants to use a spectrometer GUI .
    SPEC= False #<-- True when user wants to use a spectrometer thread.
    GUI=False #<-- True for running GUI through serial
    STACK_BUILD = [0x40,0x41,0x42,0x43,0x44,0x45] #<-- Adresses for port expanders on optocoupler stack
    PORT_BASE = 7000
    REMOTE_CTRL_PORT = PORT_BASE + 10
    #deviceconfig="C:QmixSDK/config/NemesysSetup3syr" #--> change path to device configuration folder if needed
    #/\/\/\   PARAMETERS BLOCK END  /\/\/\################################################
    ######################################################################################
    '''
    import user protocol
    '''
    protocol = __import__(lib)
    '''
    Set up communications with electrode stack and Arduino
    '''
    udpSendPid = UDP_Send.udpSend(nameID='', DesIP='127.0.0.1', DesPort=PORT_BASE +0)
    udpSendChip = UDP_Send.udpSend(nameID='', DesIP='127.0.0.1', DesPort=PORT_BASE +1)
    udpConsol = False
    if REMOTE_CTRL_PORT > 1:
        udpConsol = udpControl.udpControl(nameID='udpIDLE', RxPort=REMOTE_CTRL_PORT, callFunc=extEval)
        print 'Remote-Consol-Active on port %s\n'%(str(REMOTE_CTRL_PORT))
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
    Set up PID
    '''
    print 'PID status: %s' %(PID1)
    if PID1 == True:
        PID = threadPID.ArduPidThread(bridge=ardu,
                                      nameID='PID', #proces name
                                      Period=0.5,   #Period-time of the control-loop. PID calculation cycle time.
                                      fbPin=1,      #The analog pin of the temp sensor.
                                      outPin=10,     #The output pin  of the driver.
                                      dirPin=7      #The direction pin for the driver.
                                      )
        PID.PID.Kp = 30 # proportional control of PID
        PID.PID.Ki = 1.2 # integral of PID
        PID.PID.Kd = 0.0 # rate of change of PID (derivative)
        PID.addViewer('UDP',udpSendPid.Send) #'UDP',udpSendPid1.Send)
        PID.enIO(True) #PID.enOut = True
        ardu.gpio.pinMode(9,0)
        print 'type PID.start() to start the PID thread\n'

    '''
    Start spectrometer thread
    '''
    print 'Spectrometer Thread status: %s' %(SPEC)
    if SPEC == True:
        threadSpec = __import__('spectroThread') #delete when you place in ArduBridge. For now place thread in folder
        Spec = threadSpec.spectroThread(bridge=ardu,
                                      nameID='FLAME', #proces name
                                      Period=0.5,   #Period-time of the control-loop.
                                      device= '', # spectrometer serial number FLMS04421. If empty, first available.
                                      inttime=100000, #integration time
                                      autoexposure=False,
                                      autorepeat=False,
                                      autosave=True,
                                      dark_frames=1,
                                      enable_plot=True,
                                      output_file='Snapshot-%Y-%m-%dT%H:%M:%S%z.dat',
                                      scan_frames=1,
                                      scan_time=100000 #integration time in microseconds
                                      )
        Spec.root.mainloop()
        print 'type Spec.start() to start the FLAME thread\n'
    else:
        Spec=None
    '''
    Start spectrometer bridge
    '''
    print 'Spectrometer GUI status: %s' %(SPECGUI)
    if SPECGUI == True:
        SpecBridge = __import__('FLAME_bridge') #delete when you place in ArduBridge. For now place thread in folder
        specGui = SpecBridge.SBGUI(device= 'FLMS04421', # spectrometer serial number FLMS04421. If empty, first available.
                                      inttime=100000, #integration time
                                      autoexposure=False,
                                      autorepeat=False,
                                      autosave=True,
                                      dark_frames=1,
                                      enable_plot=True,
                                      output_file='Snapshot-%Y-%m-%dT%H:%M:%S%z.dat',
                                      scan_frames=1,
                                      scan_time=100000 #integration time in microseconds
                                      )
        SBGUI_animation = animation.FuncAnimation(specGUI.figure, specGUI.update_plot)
        specGui.root.mainloop()
        print 'Spectrometer started'
    else:
        Spec=None
    '''
    Start Nemesys syringe pump bridge
    '''
    print 'Pumps status: %s' %(PUMPS)
    if PUMPS==True:
        Pumpsbridge= __import__('Nemesys_Bridge')  #--> change protocol file if needed
        Pumps=Pumpsbridge.Nem(
                deviceconfig="C:/QmixSDK/config/Nemesys_5units_20190308", #change path to device configuration folder
                syringe_diam=[7.29,3.26,3.26,3.26,3.26], #syringe diameter, in mm
                syringe_stroke=[59,40,40,40,40] #syringe stroke length, in mm
                )
        #nem=nemesysprot.nemesys(cfg=deviceconfig)
        print 'Syringe pumps ready...'
    else:
        Pumps=None


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
    setup = protocol.Setup(ExtGpio=ExtGpio, gpio=ardu.gpio, chipViewer=udpSendChip.Send, Pumps=Pumps, Spec=Spec)
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

    setup.enOut(ELEC_EN)
    prot = protocol.Protocol(setup)

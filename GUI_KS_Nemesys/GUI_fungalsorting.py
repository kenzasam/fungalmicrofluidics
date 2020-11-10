### SHIH Microfluidics lab, 2019
### GUI to be used with ArduBridge and Protocol file
###
### On-Demand Channel operations, Single-Cell GUI, with Cetoni Nemesys low-pressure syringe pump integration
### by Kenza Samlali
### Sequence selector class by Laura Lecrerc's LLGUI
#-------------------------------------------------------------------
## >>> VERSIONS <<< ##
# v 0.1.0 - copy from Laura, adding extra function buildButtons
# v 1.0.0 - Droplet Generation buttons and functions, Droplet operations buttons and FUNCTIONS
# v 1.1.0 - Bug Fixes (error window popups when buttons pressed, integrating KeepAll in KeepAllBut)
# v 2.0.0 - Nemesys integration
# v 2.1.0 - Full pump integration
# v 2.2.0 - Add up to 5 pumps
# v 3.0.0 - Reorganized code architecture, split up in classes
#-------------------------------------------------------------------
#-------------------------------------------------------------------
#-------------------------------------------------------------------



import wx
import wx.lib.inspection
import os, sys
import pyperclip
import Tkinter, tkFileDialog
from optparse import OptionParser
from GSOF_ArduBridge import UDP_Send

'''
CODE STRUCTURE
------------------
------------------
MainFrame - MainFrame class; gathers all other panels, toolbars etc.
Menubar - Menubar class
Pumppanel - Panel class to operate syringe pumps
Operationspanel - Panel class with electrode functions
Incubationpanel - Panel class for incubation (time input, temperature input to run PID thread)
Sortingpanel - Panel class to start sorting procedure
'''

class MainFrame(wx.Frame):
    '''Create MainFrame class.'''
    def __init__(self, setup, port=-1, ip='127.0.0.1', columns=2):
        super(MainFrame, self).__init__(None, wx.ID_ANY) #, size=(400,400)
        #panel=wx.Panel(self, wx.ID_ANY)
        '''PARAMETERS'''
        pumpnrs=5
        self.Title = 'Fungal Sorting hybrid microfluidics GUI'

        '''setup sending protocol for ArduBridge Shell.'''
        udpSend = False
        if port > 1:
            udpSend = UDP_Send.udpSend(nameID='', DesIP=ip, DesPort=port)

        '''setting up wx Main Frame window.'''
        self.setup=setup
        self.SetMenuBar(MenuBar(self,pumpnrs))
        self.CreateStatusBar()
        ico=wx.Icon('shih.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        self.Bind(wx.EVT_CLOSE, self.on_quit_click)

        '''Create and populate Panel.'''
        panel=wx.Panel(self)
        #
        MAINbox = wx.BoxSizer(wx.VERTICAL)
        pumppanel = PumpPanel(panel, pumpnrs, udpSend)
        MAINbox.Add(pumppanel)
        #
        operationspanel=OperationsPanel(panel, udpSend)
        MAINbox.Add(operationspanel)
        #
        incpanel=Incubationpanel(panel, udpSend)
        MAINbox.Add(incpanel)
        #
        sortingpanel=SortingPanel(panel, udpSend)
        MAINbox.Add(sortingpanel)
        #
        panel.SetSizerAndFit(MAINbox)
        #self.Fit()
        self.Centre()


    def on_quit_click(self, event):
        """Handle close event."""
        del event
        wx.CallAfter(self.Destroy)

"""
class MainPanel(wx.Panel):
    #Panel class to contain frame widgets.
    def __init__(self):
        super(MainPanel, self).__init__()
        #Create and populate main sizer.

        #sizer for the window
        MAINbox = wx.BoxSizer(wx.VERTICAL)
        cmd_quit = wx.Button(self, id=wx.ID_EXIT)
        cmd_quit.Bind(wx.EVT_BUTTON, parent.on_quit_click)
        sizer.Add(cmd_quit)
        self.SetSizer(sizer)
"""



class PumpPanel(wx.Panel):
    def __init__(self, parent, pumpnrs,udpSend):
        super(PumpPanel, self).__init__(parent, pumpnrs)
        self.udpSend=udpSend
        self.pumpnrs=pumpnrs
        Pumpnrs=list(range(self.pumpnrs))
        choices=[str(i) for i in Pumpnrs]
        NemSizer = wx.BoxSizer(wx.VERTICAL)
        #
        line = wx.StaticLine(self,wx.ID_ANY,style=wx.LI_HORIZONTAL)
        NemSizer.Add(line, 0, wx.ALL|wx.EXPAND, 2 )
        titlebox = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, label='Pumps')
        font = wx.Font(9,wx.DEFAULT,wx.NORMAL, wx.BOLD)
        title.SetFont(font)
        titlebox.Add(title, flag=wx.ALIGN_LEFT, border=8)
        NemSizer.Add(titlebox, 0, wx.ALIGN_CENTER_VERTICAL)
        #Entry of OTHER flow rate
        boxNemf=wx.BoxSizer(wx.HORIZONTAL)
        textOtherflrt=wx.StaticText(self,  wx.ID_ANY, label='Other [uL/s]')
        boxNemf.Add(textOtherflrt, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        entryOtherflrt=wx.TextCtrl(self, wx.ID_ANY,'0.0', size=(45, -1))
        boxNemf.Add(entryOtherflrt, proportion=0.5, border=8)
        textPump=wx.StaticText(self,  wx.ID_ANY, label='Pump')
        boxNemf.Add(textPump, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        combo6 = wx.ComboBox(self, value=choices[0], choices=choices)
        combo6.Bind(wx.EVT_COMBOBOX, self.onCombo)
        boxNemf.Add(combo6, 0, wx.ALIGN_RIGHT)
        OtherBtn=wx.ToggleButton( self, label='Start', name='', size=(50,24)) #ADDED KS
        OtherBtn.Bind(wx.EVT_TOGGLEBUTTON, self.onOtherFlow)
        boxNemf.Add(OtherBtn, 0, wx.ALIGN_RIGHT)
        NemSizer.Add(boxNemf, flag=wx.LEFT, border=8)
        # pumpnrs  == 4:
        boxNeme=wx.BoxSizer(wx.HORIZONTAL)
        self.text4Otherflrt=wx.StaticText(self,  wx.ID_ANY, label='Other [uL/s]')
        boxNeme.Add(self.text4Otherflrt, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        self.entry4Otherflrt=wx.TextCtrl(self, wx.ID_ANY,'0.0', size=(45, -1))
        boxNeme.Add(self.entry4Otherflrt, proportion=0.5, border=8)
        self.text4Pump=wx.StaticText(self,  wx.ID_ANY, label='Pump')
        boxNeme.Add(self.text4Pump, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        self.combo46 = wx.ComboBox(self , value=choices[0], choices=choices)
        self.combo46.Bind(wx.EVT_COMBOBOX, self.onCombo)
        boxNeme.Add(self.combo46, 0, wx.ALIGN_RIGHT)
        self.Other4Btn=wx.ToggleButton( self, label='Start', name='', size=(50,24)) #ADDED KS
        self.Other4Btn.Bind(wx.EVT_TOGGLEBUTTON, self.onOtherFlow)
        boxNeme.Add(self.Other4Btn, 0, wx.ALIGN_RIGHT)
        # pumpnrs == 5:
        boxNemd=wx.BoxSizer(wx.HORIZONTAL)
        self.text5Otherflrt=wx.StaticText(self,  wx.ID_ANY, label='Other [uL/s]')
        boxNemd.Add(self.text5Otherflrt, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        self.entry5Otherflrt=wx.TextCtrl(self, wx.ID_ANY,'0.0', size=(45, -1))
        boxNemd.Add(self.entry5Otherflrt, proportion=0.5, border=8)
        self.text5Pump=wx.StaticText(self,  wx.ID_ANY, label='Pump ')
        boxNemd.Add(self.text5Pump, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        self.combo56 = wx.ComboBox(self, value=choices[0], choices=choices)
        self.combo56.Bind(wx.EVT_COMBOBOX, self.onCombo)
        boxNemd.Add(self.combo56, 0, wx.ALIGN_RIGHT)
        self.Other5Btn=wx.ToggleButton( self, label='Start', name='', size=(50,24)) #ADDED KS
        self.Other5Btn.Bind(wx.EVT_TOGGLEBUTTON, self.onOtherFlow)
        boxNemd.Add(self.Other5Btn, 0, wx.ALIGN_RIGHT)
        if pumpnrs  == 4:
            NemSizer.Add(boxNemd, flag=wx.LEFT, border=8)
        elif pumpnrs  == 5:
            NemSizer.Add(boxNemd, flag=wx.LEFT, border=8)
            NemSizer.Add(boxNeme, flag=wx.LEFT, border=8)
        #Entry of Oil consant flow rate
        boxNema=wx.BoxSizer(wx.HORIZONTAL)
        textOilflrt=wx.StaticText(self,  wx.ID_ANY, label='Oil [uL/s]')
        boxNema.Add(textOilflrt, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        entryOilflrt=wx.TextCtrl(self, wx.ID_ANY,'0.0', size=(45, -1))
        boxNema.Add(entryOilflrt, proportion=0.5, border=8)
        boxNema.Add(textPump, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        boxNema.Add(combo6, 0, wx.ALIGN_RIGHT)
        OilBtn=wx.ToggleButton( self, label='Start', name='', size=(50,24)) #ADDED KS
        OilBtn.Bind(wx.EVT_TOGGLEBUTTON, self.onOilFlow)
        boxNema.Add(OilBtn, 0, wx.ALIGN_RIGHT)
        NemSizer.Add(boxNema, flag=wx.LEFT, border=8)
        ##Entry of Flowrate continuous aqueous
        boxNemc=wx.BoxSizer(wx.HORIZONTAL)
        textAqflrt=wx.StaticText(self,  wx.ID_ANY, label='Aq [uL/s]')
        boxNemc.Add(textAqflrt, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        entryAqflrt=wx.TextCtrl(self, wx.ID_ANY,'0.0', size=(45, -1))
        boxNemc.Add(entryAqflrt, proportion=0.5, border=8)
        boxNemc.Add(textPump, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        boxNemc.Add(combo6, 0, wx.ALIGN_RIGHT)
        AqBtn=wx.ToggleButton( self, label='Start', name='', size=(50,24)) #ADDED KS
        AqBtn.Bind(wx.EVT_TOGGLEBUTTON, self.onAqFlow)
        boxNemc.Add(AqBtn, 0, wx.ALIGN_RIGHT)
        NemSizer.Add(boxNemc, flag=wx.LEFT, border=8)
        ##
        self.SetSizer(NemSizer)
        #MAINbox.Add(NemSizer, 0, wx.ALL)
        self.SetBackgroundColour('#6f8089')

    def onOilFlow(self, event):
        flrt=float(self.entryOilflrt.GetValue())
        print flrt
        pumpID=int(self.combo1.GetValue())
        print pumpID
        if flrt == 0.0:
            wx.MessageDialog(self, "Enter a correct flowrate, and select a pump", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        else:
            state = event.GetEventObject().GetValue()
            if state == True:
               print "on"
               event.GetEventObject().SetLabel("Stop")
               s = 'setup.nem.pump_generate_flow(setup.nem.pumpID(%d),%f)'%(pumpID,flrt)
               pyperclip.copy(s)
               if self.udpSend != False:
                   self.udpSend.Send(s)
            else:
               print "off"
               event.GetEventObject().SetLabel("Start")
               s = 'setup.nem.pump_stop(setup.nem.pumpID(%d))'%(pumpID) #\'%s\'
               pyperclip.copy(s)
               if self.udpSend != False:
                   self.udpSend.Send(s)
    def onAqFlow(self, event):
        flrt=float(self.entryAqflrt.GetValue())
        print flrt
        pumpID=int(self.combo3.GetValue())
        print pumpID
        if flrt == 0.0:
            wx.MessageDialog(self, "Enter a correct flowrate, and select a pump", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        else:
            state = event.GetEventObject().GetValue()
            if state == True:
               print "on"
               event.GetEventObject().SetLabel("Stop")
               s = 'setup.nem.pump_generate_flow(setup.nem.pumpID(%d),%f)'%(pumpID,flrt)
               pyperclip.copy(s)
               if self.udpSend != False:
                   self.udpSend.Send(s)
            else:
               print "off"
               event.GetEventObject().SetLabel("Start")
               s = 'setup.nem.pump_stop(setup.nem.pumpID(%d))'%(pumpID) #\'%s\'
               pyperclip.copy(s)
               if self.udpSend != False:
                   self.udpSend.Send(s)
    def onOtherFlow(self, event):
        flrt=float(entryOtherflrt.GetValue())
        print flrt
        pumpID=int(combo4.GetValue())
        print pumpID
        if flrt == 0.0:
            wx.MessageDialog(self, "Enter a correct flowrate, and select a pump", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        else:
            state = event.GetEventObject().GetValue()
            if state == True:
               print "on"
               event.GetEventObject().SetLabel("Stop")
               s = 'setup.nem.pump_generate_flow(setup.nem.pumpID(%d),%f)'%(pumpID,flrt)
               pyperclip.copy(s)
               if self.udpSend != False:
                   self.udpSend.Send(s)
            else:
               print "off"
               event.GetEventObject().SetLabel("Start")
               s = 'setup.nem.pump_stop(setup.nem.pumpID(%d))'%(pumpID) #\'%s\'
               pyperclip.copy(s)
               if self.udpSend != False:
                   self.udpSend.Send(s)
    def onCombo(self, event):
        print 'pump changed'

class OperationsPanel(wx.Panel):
    def __init__(self,parent,udpSend):
        wx.Panel.__init__(self,parent,udpSend)
        self.udpSend=udpSend
        """Create and populate main sizer."""
        fnSizer = wx.BoxSizer(wx.VERTICAL)
        #
        line = wx.StaticLine(self,wx.ID_ANY,style=wx.LI_HORIZONTAL)
        fnSizer.Add( line, 0, wx.ALL|wx.EXPAND, 2 )
        titlebox  = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, label='Electrode Functions')
        font = wx.Font(9,wx.DEFAULT,wx.NORMAL, wx.BOLD)
        title.SetFont(font)
        titlebox.Add(title, flag=wx.ALIGN_LEFT, border=8)
        fnSizer.Add(titlebox, 0, wx.ALIGN_CENTER_VERTICAL)
        #Sort
        box1=wx.BoxSizer(wx.HORIZONTAL)
        self.SortBtn=wx.Button( self, label='Sort', name='Sort()', size=(70,24)) #ADDED KS
        self.SortBtn.Bind(wx.EVT_BUTTON, self.onSort)
        box1.Add(self.SortBtn, flag=wx.RIGHT, border=8)
        self.text1=wx.StaticText(self,  wx.ID_ANY, label='t [s]  ')
        box1.Add(self.text1, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        self.entry1=wx.TextCtrl(self, wx.ID_ANY,'0', size=(30, -1))
        box1.Add(self.entry1, proportion=1)
        fnSizer.Add(box1, flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(fnSizer)
        self.SetBackgroundColour('#32a852')


    def onSort(self, event):
        try:
            t=int(float(self.entry1.GetValue()))
        except:
            wx.MessageDialog(self, "Enter a number", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        s = 'setup.Sorting(%d)'%(t)
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)

class Incubationpanel(wx.Panel):
    def __init__(self, parent,udpSend):
        wx.Panel.__init__(self,parent,udpSend)
        self.udpSend=udpSend
        """Create and populate main sizer."""
        incSizer = wx.BoxSizer(wx.VERTICAL)
        #
        line = wx.StaticLine(self,wx.ID_ANY,style=wx.LI_HORIZONTAL)
        incSizer.Add( line, 0, wx.ALL|wx.EXPAND, 2 )
        titlebox  = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, label='Droplet Incubation')
        font = wx.Font(9,wx.DEFAULT,wx.NORMAL, wx.BOLD)
        title.SetFont(font)
        titlebox.Add(title, flag=wx.ALIGN_LEFT, border=8)
        incSizer.Add(titlebox, 0, wx.ALIGN_CENTER_VERTICAL)
        #pid
        box3=wx.BoxSizer(wx.HORIZONTAL)
        self.pidBtn=wx.Button( self, label='Show PID control', name='PID.start()', size=(70,24))
        self.pidBtn.Bind(wx.EVT_BUTTON, self.onPid)
        box3.Add(self.pidBtn, flag=wx.RIGHT, border=8)
        self.IncBtn=wx.Button( self, label='Start', name='PID.start()', size=(70,24))
        self.IncBtn.Bind(wx.EVT_BUTTON, self.onIncubate)
        box3.Add(self.IncBtn, flag=wx.RIGHT, border=8)
        incSizer.Add(box3, flag=wx.ALIGN_CENTER_VERTICAL)
        #Temperature
        box1=wx.BoxSizer(wx.HORIZONTAL)
        self.text1=wx.StaticText(self,  wx.ID_ANY, label='Temperature [C]:')
        box1.Add(self.text1, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        self.entry1=wx.TextCtrl(self, wx.ID_ANY,'0', size=(30, -1))
        box1.Add(self.entry1, proportion=1)
        incSizer.Add(box1, flag=wx.ALIGN_CENTER_VERTICAL)
        #Time
        box2=wx.BoxSizer(wx.HORIZONTAL)
        self.text2=wx.StaticText(self,  wx.ID_ANY, label='Time [min]:')
        box2.Add(self.text2, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        self.entry2=wx.TextCtrl(self, wx.ID_ANY,'0', size=(30, -1))
        box2.Add(self.entry2, proportion=1)
        incSizer.Add(box2, flag=wx.ALIGN_CENTER_VERTICAL)
        #imaging pipeline
        box4=wx.BoxSizer(wx.HORIZONTAL)
        self.imgsetupBtn=wx.Button( self, label='Show PID control', name='PID.start()', size=(70,24))
        self.imgsetupBtn.Bind(wx.EVT_BUTTON, self.onImgsetup)
        box4.Add(self.imgsetupBtn, flag=wx.RIGHT, border=8)
        self.ImgBtn=wx.Button( self, label='Start', name='PID.start()', size=(70,24))
        self.ImgBtn.Bind(wx.EVT_BUTTON, self.onImage)
        box4.Add(self.ImgBtn, flag=wx.RIGHT, border=8)
        incSizer.Add(box4, flag=wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(incSizer)
        self.SetBackgroundColour('#c597c72')

    def onIncubate(self,event):
        try:
            temp=int(float(self.entry1.GetValue()))
            t=int(float(self.entry2.GetValue()))
        except:
            wx.MessageDialog(self, "Enter a valid temperature", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        s = 'setup.PID.Incubation(%d,%d)'%(temp,t)
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)

    def onPid(self,event):
        s = 'setup.PID.plot()'
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)

    def onImgsetup(self, event):
        return

    def onImage(self, event):
        return


class SortingPanel(wx.Panel):
    def __init__(self,paren,udpSend):
        wx.Panel.__init__(self,parent,udpSend)
        ########################################
        #############FUNCTIONS#####sizer########
        #######################################
        self.udpSend=udpSend
        """Create and populate main sizer."""
        srtSizer = wx.BoxSizer(wx.VERTICAL)
        #
        line = wx.StaticLine(self,wx.ID_ANY,style=wx.LI_HORIZONTAL)
        srtSizer.Add( line, 0, wx.ALL|wx.EXPAND, 2 )
        titlebox  = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, label='Droplet Sorting')
        font = wx.Font(9,wx.DEFAULT,wx.NORMAL, wx.BOLD)
        title.SetFont(font)
        titlebox.Add(title, flag=wx.ALIGN_LEFT, border=8)
        srtSizer.Add(titlebox, 0, wx.ALIGN_CENTER_VERTICAL)
        #Sort
        box1=wx.BoxSizer(wx.HORIZONTAL)
        self.StartSortBtn=wx.Button( self, label='Start Sorting', name='Sort()', size=(70,24)) #ADDED KS
        self.StartSortBtn.Bind(wx.EVT_BUTTON, self.onStart)
        box1.Add(self.StartSortBtn, flag=wx.RIGHT, border=8)
        self.text1=wx.StaticText(self,  wx.ID_ANY, label='t [s]  ')
        box1.Add(self.text1, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        self.entry1=wx.TextCtrl(self, wx.ID_ANY,'0', size=(30, -1))
        box1.Add(self.entry1, proportion=1)
        srtSizer.Add(box1, flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(srtSizer)
        self.SetBackgroundColour('#f2dd88')

    def onStart(self, event):
        try:
            t=int(float(self.entry1.GetValue()))
        except:
            wx.MessageDialog(self, "Enter a number", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        s = 'setup.Sorting(%d)'%(t)
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)

class MenuBar(wx.MenuBar):
    """Create the menu bar."""
    def __init__(self, parent, pumpnrs):
        wx.MenuBar.__init__(self)
        self.pumpnrs=pumpnrs
        Pumpnrs=list(range(self.pumpnrs))
        # File menu
        #menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        self.fileItem1 = fileMenu.Append(wx.ID_EXIT,'Quit')
        self.Bind(wx.EVT_MENU, self.onQuit, self.fileItem1)
        #menubar.Append(fileMenu, 'File')
        arduMenu = wx.Menu()
        self.arduItem1 = arduMenu.Append(wx.ID_ANY,'Open Port', 'openPort()')
        self.Bind(wx.EVT_MENU, self.onRemoteOpenPort,self.arduItem1)
        self.arduItem2 = arduMenu.Append(wx.ID_ANY, 'Close Port', 'closePort()')
        self.Bind(wx.EVT_MENU, self.onRemoteClosePort,self.arduItem2)
        self.arduItem3 = arduMenu.Append(wx.ID_ANY, 'Close Arduino comm', 'close()')
        self.Bind(wx.EVT_MENU, self.onCloseArdu,self.arduItem3)
        #menubar.Append(arduMenu, 'Ardu')
        nemMenu = wx.Menu()
        self.nemItem1 = nemMenu.Append(wx.ID_ANY, 'Open NeMESYS bus', 'nem.bus_open()')
        self.Bind(wx.EVT_MENU, self.onOpenNem, self.nemItem1)
        self.nemItem2 = nemMenu.Append(wx.ID_ANY, 'Close NeMESYS bus', 'nem.bus_close()')
        self.Bind(wx.EVT_MENU, self.onCloseNem, self.nemItem2)
        stopMenu = wx.Menu()
        self.stopAll = stopMenu.Append(wx.ID_ANY, 'Stop All', '')
        self.Bind(wx.EVT_MENU, self.onStopPumps, self.stopAll)
        self.stopItem=[]
        for i in Pumpnrs:
            self.stopItem.append(stopMenu.Append(wx.ID_ANY, str(i), str(i)))
            self.Bind(wx.EVT_MENU, self.onStopOnePump, self.stopItem[i])
        nemMenu.Append(wx.ID_ANY, 'Stop Pumps', stopMenu)
        calibrateMenu = wx.Menu()
        self.calibrateItem=[]
        for i in Pumpnrs:
            self.calibrateItem.append(calibrateMenu.Append(wx.ID_ANY, str(i), str(i)))
            self.Bind(wx.EVT_MENU, self.onCalibratePump, self.calibrateItem[i])
        nemMenu.Append(wx.ID_ANY, 'Calibrate', calibrateMenu)
        #menubar.Append(nemMenu, 'Nemesys')
        #self.SetMenuBar(menubar)
        ##############
    def onQuit(self,event):
        self.Close()
    def onCloseArdu(self,event):
        s= 'close()'
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)
    def onCloseNem(self,event):
        s= 'setup.bus.close()'
        self.setup.pumpsObjList[pumpID]
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)
        for pump in range(2):
            f= str(setup.pumpsObjList[pump].stop_pumping())
            pyperclip.copy(f)
            if self.udpSend != False:
                self.udpSend.Send(f)
    def onOpenNem(self,event):
        s= 'setup.bus.open()'
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)
    def onStopOnePump(self,event):
        item=self.GetMenuBar().FindItemById(event.GetId())
        s = 'setup.nem.pump_stop(setup.nem.pumpID(%s))' %(str(item.GetText()))
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)
    def onStopPumps(self,event):
        s= 'setup.nem.pump_stop_all()'
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)
    def onCalibratePump(self,event):
        item=self.GetMenuBar().FindItemById(event.GetId())
        s = 'setup.nem.pump_calibration(setup.nem.pumpID(%s))' %(str(item.GetText()))
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)
    def onRemoteOpenPort(self, event):
        s = 'ardu.OpenClosePort(1)'
        pyperclip.copy(s)
        if self.udpSend != False:
                self.udpSend.Send(s)
    def onRemoteClosePort(self, event):
        s = 'ardu.OpenClosePort(0)'
        pyperclip.copy(s)
        if self.udpSend != False:
                self.udpSend.Send(s)



if __name__ == "GUI_KS_Nemesys.GUI_KS_SC_nemesys" or "__main__":

    def fileChooser():
        root = Tkinter.Tk()
        root.withdraw()
        filename = tkFileDialog.askopenfilename()
        return filename
    ver = '3.1.2'
    date = '28/10/2020'
    print 'GUI: Protocol GUI Ver:%s'%(ver)
    print 'Copyright: Kenza Samlali, 2020'
    #Command line option parser

    parser = OptionParser()
    parser.add_option('-p', '--protocol', dest='prot', help='TBD', type='string', default='Demoprotocol')
    parser.add_option('-u', '--port', dest='port', help='Remote port to send the commands', type='int', default=7010)
    parser.add_option('-i', '--ip', dest='ip', help='Remote ip to send the commands', type='string', default='127.0.0.1')
    (options, args) = parser.parse_args()
    path = os.path.split(options.prot)

    #file chooser opens if no other file was specified in the additional text file
    if path[1] == 'Demoprotocol':
        newPath = fileChooser()
        path = os.path.split(newPath)
    else:
        print 'Loading protocol specified in accompanying address file, which is in your folder.'

    #parser resumes
    lib = str(path[1])[:-3]
    path = path[0]
    sys.path.append(path)
    #lib = options.prot
    print 'Importing: %s'%(lib)
    print 'Using remote-ip:port -> %s:%d'%(options.ip, options.port)
    protocol = __import__(lib)
    """for on Mac testing
    lib="/Users/kenza/OneDrive - Concordia University - Canada/CASB-PhD/Automation/PYTHON/nemesys/"
    sys.path.append(os.path.abspath(lib))
    protocol= __import__("protocol_KS_wizzardv4_nemesys5")
    """
    setup = protocol.Setup(ExtGpio=False, gpio=False, chipViewer=False, Pumps=False, Spec=False, PID=False)

    #setup = protocol.Setup(ExtGpio=False, gpio=False, chipViewer=False, Nemesys=False)
    #setup = protocol.Setup(ExtGpio=False, gpio=False, chipViewer=False, magPin=0)
    #setup.enOut(True)
    app = wx.App(False)
    frame = MainFrame(setup, ip=options.ip, port=options.port)
    frame.Show()
    wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

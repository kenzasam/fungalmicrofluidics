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
SHIH Microfluidics lab, 2021
GUI to be used with GSOF_ArduBridge Ardubrige and Protocol file

A GUI to operate a microfluidic system: On-Demand electrode operations (see GSOF_Ardubridge), Nemesys low-pressure syringe pump (Cetoni GmBh) operation,
FLAME spectrometer (Ocean Optics) operation, TEC/Peltier operation with PID temperature control.

Credits:
Code written by Kenza Samlali
shih.ico: by Steve C.C. SHIH
pause.png, play.png, stop.png: Freepik (CC license)
Splash screen: designed by Kenza Samlali
#-------------------------------------------------------------------
## >>> VERSIONS <<< ##
# v 0.1. - copy from Laura (LLGUI, ArduBridge, GPLv3), adding extra function buildButtons
# v 1.0. - Droplet Generation buttons and functions, Droplet operations buttons and FUNCTIONS
# v 1.1. - Bug Fixes (error window popups when buttons pressed, integrating KeepAll in KeepAllBut)
# v 2.0. - Nemesys integration
# v 2.1. - Full pump integration
# v 2.2. - Add up to 5 pumps
# v 3.0. - Reorganized code architecture, split up in classes
# v 3.1. - Spectrometer, PID/incubation integration
# v 3.1. - 
#-------------------------------------------------------------------
"""
import wx
import wx.adv
import wx.lib.inspection
import wx.lib.agw.foldpanelbar as fpb
import time
import os, sys
import pyperclip
import Tkinter, tkFileDialog
from optparse import OptionParser
from GSOF_ArduBridge import UDP_Send
import subprocess
# for py3 use importlib.resources, https://realpython.com/python-import/#resource-imports
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
    def __init__(self, setup, imgViewer, path, port=-1, ip='127.0.0.1', columns=2):
        super(MainFrame, self).__init__(None, wx.ID_ANY|wx.BORDER_RAISED) #, size=(400,400)
        #panel=wx.Panel(self, wx.ID_ANY)
        '''PARAMETERS'''
        pumpnrs=5
        global build
        build = path
        self.Title = 'Fungal Sorting hybrid microfluidics GUI'
        self.cvwr  = os.path.join(build,'wxChipViewer_fungalmicrofluidics.bat') # Path to Chip Viewer file
        self.tvwr = os.path.join(buildPath,'wxTempViewer_fungalmicrofluidics.bat') # Path to PID control temperature plotting file
        self.svwr = os.path.join(buildPath,'wxSpecViewer_fungalmicrofluidics.bat') #Path to spectrum plotting file
        self.imgvwr = imgViewer #Path to Imaging pipeline
        '''setup sending protocol for ArduBridge Shell.'''
        udpSend = False
        if port > 1:
            udpSend = UDP_Send.udpSend(nameID='', DesIP=ip, DesPort=port)
        '''setting up wx Main Frame window.'''
        self.setup=setup
        self.CreateStatusBar()
        ico = wx.Icon(os.path.join(build,'shih.ico'), wx.BITMAP_TYPE_ICO)
        self.SetIcon(ico)
        self.Bind(wx.EVT_CLOSE, self.on_quit_click)
        #
        '''Create and populate Panels.'''
        MAINbox = wx.BoxSizer(wx.VERTICAL)
        MAINbox2 = wx.BoxSizer(wx.VERTICAL)
        self.pumppanel = PumpPanel(self, pumpnrs, udpSend)
        MAINbox.Add(self.pumppanel, 1, wx.EXPAND|wx.ALL, 2)
        self.operationspanel = OperationsPanel(self, udpSend)
        MAINbox.Add(self.operationspanel, 1, wx.EXPAND|wx.ALL, 2)
        #PID = self.PID_status(menubar)
        '''
        self.incpanel = IncubationPanel(self, self.imgvwr, udpSend)
        MAINbox.Add(self.incpanel, 1, wx.EXPAND|wx.ALL, 2)
        self.incpanel.Disable()#
        '''
        self.sortingpanel = SortingPanel(self, udpSend)
        #self.Bind(wx.EVT_CHECKBOX, self.sortingpanel.onCheck)
        MAINbox2.Add(self.sortingpanel, 1, wx.EXPAND|wx.ALL, 2)
        self.sortingpanel.Disable()#
        
        '''Create and populate Menubar.'''
        #menubar = MenuBar(pumpnrs, self.tvwr, self.svwr, self.cvwr, udpSend, self.sortingpanel, self.incpanel)
        menubar = MenuBar(pumpnrs, self.tvwr, self.svwr, self.cvwr, udpSend, self.sortingpanel)

        self.Bind(wx.EVT_MENU, menubar.onQuit, menubar.fileItem1)
        self.Bind(wx.EVT_MENU, menubar.onCloseAll, menubar.fileItem2)
        self.Bind(wx.EVT_MENU, menubar.onRemoteOpenPort, menubar.arduItem1)
        self.Bind(wx.EVT_MENU, menubar.onRemoteClosePort, menubar.arduItem2)
        self.Bind(wx.EVT_MENU, menubar.onChipVwr, menubar.arduItem3)
        self.Bind(wx.EVT_MENU, menubar.onOpenNem, menubar.nemItem1)
        self.Bind(wx.EVT_MENU, menubar.onCloseNem, menubar.nemItem2)
        self.Bind(wx.EVT_MENU, menubar.onStopPumps, menubar.stopAll)
        '''
        self.Bind(wx.EVT_MENU, menubar.onPIDstart, menubar.pidItem1)
        self.Bind(wx.EVT_MENU, menubar.onPIDpause, menubar.pidItem2)
        self.Bind(wx.EVT_MENU, menubar.onPIDstop, menubar.pidItem3)
        self.Bind(wx.EVT_MENU, menubar.onPIDVwr, menubar.pidItem4)
        '''
        self.Bind(wx.EVT_MENU, menubar.onStartSpec, menubar.specItem1)
        self.Bind(wx.EVT_MENU, menubar.onStopSpec, menubar.specItem2)
        self.Bind(wx.EVT_MENU, menubar.onSpecVwr, menubar.specItem3)
        Pumpnrs = list(range(pumpnrs))
        for i in Pumpnrs:
            self.Bind(wx.EVT_MENU, menubar.onStopOnePump, menubar.stopItem[i])
            self.Bind(wx.EVT_MENU, menubar.onCalibratePump, menubar.calibrateItem[i])
        
        self.SetMenuBar(menubar)
        #
        appbox = wx.BoxSizer(wx.HORIZONTAL)
        appbox.Add(MAINbox, 1, wx.EXPAND|wx.ALL, 2)
        appbox.Add(MAINbox2, 1, wx.EXPAND|wx.ALL, 2)
        self.SetSizerAndFit(appbox)
        #self.SetSizerAndFit(MAINbox)
        #self.Centre()
        #foldingpanel bar see https://wxpython.org/Phoenix/docs/html/wx.lib.agw.foldpanelbar.html
        

    def on_quit_click(self, event):
        """Handle close event."""
        del event
        wx.CallAfter(self.Destroy)

class PumpPanel(wx.Panel):
    """ panel class for Nemesys pump operation"""
    def __init__(self, parent, pumpnrs,udpSend):
        super(PumpPanel, self).__init__(parent, pumpnrs)
        self.udpSend=udpSend
        self.pumpnrs=pumpnrs
        Pumpnrs=list(range(self.pumpnrs))
        choices=[str(i) for i in Pumpnrs]
        NemSizer = wx.BoxSizer(wx.VERTICAL)
        #
        NemSizer.AddSpacer(5)
        titlebox = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, label='Pumps')
        font = wx.Font(9,wx.DEFAULT,wx.NORMAL, wx.BOLD)
        title.SetFont(font)
        titlebox.Add(title, flag=wx.ALIGN_LEFT, border=8)
        NemSizer.Add(titlebox, 0, wx.ALIGN_CENTER_VERTICAL)
        NemSizer.AddSpacer(10)
        # adding pumps
        for i in Pumpnrs:
            boxNem=wx.BoxSizer(wx.HORIZONTAL)
            flrt=wx.StaticText(self,  wx.ID_ANY, label='Flow [uL/s]')
            boxNem.Add(flrt, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
            entryflrt=wx.TextCtrl(self, wx.ID_ANY,'0.0', size=(45, -1))
            boxNem.Add(entryflrt, proportion=0.5, border=8)
            textpump = 'Pump #'+ str(i)
            textPump = wx.StaticText(self, wx.ID_ANY, label=textpump)
            boxNem.Add(textPump, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
            Btn = wx.ToggleButton( self, label='Start', name='', size=(50,24))
            Btn.Bind(wx.EVT_TOGGLEBUTTON, lambda event, dropid=i, entry=entryflrt: self.onStartFlow(event, dropid, entry)) 
            boxNem.Add(Btn, 0, wx.ALIGN_RIGHT)
            NemSizer.Add(boxNem, flag=wx.LEFT|wx.EXPAND, border=8)
        #
        self.SetSizer(NemSizer)
        NemSizer.AddSpacer(5)
    
    def onStartFlow(self, event, pump, entry):
        flrt = float(entry.GetValue())
        if flrt == 0.0:
            wx.MessageDialog(self, "Enter a correct flowrate, and select a pump", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        else:
            state = event.GetEventObject().GetValue()
            if state == True:
               print "on"
               event.GetEventObject().SetLabel("Stop")
               s = 'setup.nem.pump_generate_flow(setup.nem.pumpID(%d),%f)'%(pump,flrt)
               pyperclip.copy(s)
               if self.udpSend != False:
                   self.udpSend.Send(s)
            else:
               print "off"
               event.GetEventObject().SetLabel("Start")
               s = 'setup.nem.pump_stop(setup.nem.pumpID(%d))'%(pump) #\'%s\'
               pyperclip.copy(s)
               if self.udpSend != False:
                   self.udpSend.Send(s)

class OperationsPanel(wx.Panel):
    """Panel class for user set functions for electrode actuation"""
    def __init__(self, parent, udpSend):
        super(OperationsPanel, self).__init__(parent)
        #wx.Panel.__init__(self,parent,udpSend)
        self.udpSend = udpSend
        """Create and populate main sizer."""
        fnSizer = wx.BoxSizer(wx.VERTICAL)
        #
        fnSizer.AddSpacer(5)
        titlebox  = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, label='Electrode Functions')
        font = wx.Font(9,wx.DEFAULT,wx.NORMAL, wx.BOLD)
        title.SetFont(font)
        titlebox.Add(title, flag=wx.ALIGN_LEFT, border=8)
        fnSizer.Add(titlebox, 0, wx.ALIGN_CENTER_VERTICAL)
        fnSizer.AddSpacer(10)
        #self.vwrBtn=wx.Button( self, label='Show chip viewer', name='wxChipViewer',style=wx.BU_EXACTFIT)
        #self.vwrBtn.Bind(wx.EVT_BUTTON, self.onVwr)
        #fnSizer.Add(self.vwrBtn, flag=wx.RIGHT, border=8)
        #sorting
        box=wx.BoxSizer(wx.HORIZONTAL)
        onTime=wx.StaticText(self,  wx.ID_ANY, label='onTime [s]')
        box.Add(onTime, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        self.entry=wx.TextCtrl(self, wx.ID_ANY,'0', size=(45, -1))
        fnSizer.Add(box, flag=wx.ALIGN_CENTER_VERTICAL)
        fnSizer.AddSpacer(5)
        box.Add(self.entry, proportion=0.5, border=8)
        box1=wx.BoxSizer(wx.HORIZONTAL)
        self.SortBtn=wx.Button( self, 1, label='Sort v1', name='Sort()', size=(70,24)) #ADDED KS
        self.SortBtn.Bind(wx.EVT_BUTTON, self.onSort)
        box1.Add(self.SortBtn, flag=wx.RIGHT, border=8)
        self.SortBtn2=wx.Button( self, 2, label='Sort v2', name='Sort()', size=(70,24)) #ADDED KS
        self.SortBtn2.Bind(wx.EVT_BUTTON, self.onSort)
        box1.Add(self.SortBtn2, flag=wx.RIGHT, border=8)
        '''
        self.text1=wx.StaticText(self,  wx.ID_ANY, label='t [s]  ')
        box1.Add(self.text1, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        self.entry1=wx.TextCtrl(self, wx.ID_ANY,'0', size=(30, -1))
        box1.Add(self.entry1, proportion=1)
        '''
        fnSizer.Add(box1, flag=wx.ALIGN_CENTER_VERTICAL)
        fnSizer.AddSpacer(5)
        self.SetSizer(fnSizer)
        #self.SetBackgroundColour('#32a852')

    def onSort(self, event):
        t=int(self.entry.GetValue())
        s = 'setup.sortseq(%d, %d)'%(event.GetId(), t)
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)

class IncubationPanel(wx.Panel):
    """Panel class for setting incubation parameters (temperature, time, PID control)
    and imaging pipeline"""
    def __init__(self, parent, imvwr, udpSend):
        super(IncubationPanel, self).__init__(parent)
        #wx.Panel.__init__(self,parent,udpSend)
        self.udpSend = udpSend
        #self.menu = menubar
        self.imgvwr = imvwr
        """Create and populate main sizer."""
        incSizer = wx.BoxSizer(wx.VERTICAL)
        #
        incSizer.AddSpacer(5)
        titlebox  = wx.BoxSizer(wx.HORIZONTAL)
        title = wx.StaticText(self, label='Droplet Incubation')
        font = wx.Font(9,wx.DEFAULT,wx.NORMAL, wx.BOLD)
        title.SetFont(font)
        titlebox.Add(title, flag=wx.ALIGN_LEFT, border=8)
        incSizer.Add(titlebox, 0, wx.ALIGN_CENTER_VERTICAL)
        incSizer.AddSpacer(10)
        #Temperature
        box1=wx.BoxSizer(wx.HORIZONTAL)
        self.text1=wx.StaticText(self,  wx.ID_ANY, label='Temperature [C]:')
        box1.Add(self.text1, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        self.entry1=wx.TextCtrl(self, wx.ID_ANY,'0', size=(30, -1))
        box1.Add(self.entry1, proportion=1)
        incSizer.Add(box1, flag=wx.ALIGN_CENTER_VERTICAL)
        #Time
        box2=wx.BoxSizer(wx.HORIZONTAL)
        self.text2=wx.StaticText(self,  wx.ID_ANY, label='Max. Time [min]:')
        box2.Add(self.text2, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        self.entry2=wx.TextCtrl(self, wx.ID_ANY,'0', size=(30, -1))
        box2.Add(self.entry2, proportion=1)
        incSizer.Add(box2, flag=wx.ALIGN_CENTER_VERTICAL)
        #incubate
        box3=wx.BoxSizer(wx.HORIZONTAL)
        self.IncBtn=wx.Button( self, label='Start incubation', name='', style=wx.BU_EXACTFIT)
        self.IncBtn.Bind(wx.EVT_BUTTON, self.onIncubate)
        box3.Add(self.IncBtn, flag=wx.RIGHT, border=8)
        incSizer.Add(box3, flag=wx.ALIGN_CENTER_VERTICAL)
        #spacer
        #incSizer.AddSpacer(10)
        line = wx.StaticLine(self,wx.ID_ANY,style=wx.LI_HORIZONTAL)
        incSizer.Add( line, 0, wx.ALL|wx.EXPAND, 2 )
        #imaging pipeline
        box4=wx.BoxSizer(wx.HORIZONTAL)
        self.imgsetupBtn=wx.Button( self, label='Start imaging pipeline ...', name='PID.start()', style=wx.BU_EXACTFIT)
        self.imgsetupBtn.Bind(wx.EVT_BUTTON, self.onShowMimic)
        box4.Add(self.imgsetupBtn, flag=wx.RIGHT, border=8)
        incSizer.Add(box4, flag=wx.ALIGN_CENTER_VERTICAL)
        incSizer.AddSpacer(5)
        self.SetSizer(incSizer)
        self.SetBackgroundColour('#c597c72')

    def onShowMimic(self, event):
        """Imaging pop-up window"""
        cmd = str(self.imgvwr)
        print('Opening:'+ cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def onIncubate(self, event):
        status = MenuBar.PID_status
        if status != True:
            wx.MessageDialog(self, "Please first start the PID", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        else:
            try:
                temp=int(float(self.entry1.GetValue()))
                time=int(float(self.entry2.GetValue()))
                RC=0.5
            except:
                wx.MessageDialog(self, "Enter a valid temperature and time", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
            s = 'setup.incubation(%d, %d, %d)'%(RC, temp,time)
            pyperclip.copy(s)
            if self.udpSend != False:
                self.udpSend.Send(s)

    def onImage(self, event):
        return

class SortingPanel(wx.Panel):
    """ Panel class for droplet sorting: starting spectrometer, sorting electrode sequences"""
    def __init__(self, parent, udpSend):
        super(SortingPanel, self).__init__(parent)
        self.udpSend = udpSend
        #self.menu = menubar

        def spacer(sizer):
            line = wx.StaticLine(self,wx.ID_ANY,style=wx.LI_HORIZONTAL)
            sizer.AddSpacer(10)
            sizer.Add( line, 0, wx.ALL|wx.EXPAND, 2 )
            sizer.AddSpacer(10)

        """Create and populate main sizer."""
        srtSizer = wx.BoxSizer(wx.VERTICAL)
        srtSizer.AddSpacer(5)
        titlebox1  = wx.BoxSizer(wx.HORIZONTAL)
        title1 = wx.StaticText(self, label='Droplet Sorting')
        font = wx.Font(9,wx.DEFAULT,wx.NORMAL, wx.BOLD)
        title1.SetFont(font)
        titlebox1.Add(title1, flag=wx.ALIGN_LEFT, border=8)
        srtSizer.Add(titlebox1, 0, wx.ALIGN_CENTER_VERTICAL)
        srtSizer.AddSpacer(10)
        #spectrometer
        # Start, Background
        titlebox2  = wx.BoxSizer(wx.HORIZONTAL)
        title2 = wx.StaticText(self, label='Spectral Measurement')
        font2 = wx.Font(9,wx.DEFAULT,wx.NORMAL,wx.NORMAL)
        title2.SetFont(font)
        titlebox2.Add(title2, flag=wx.ALIGN_LEFT, border=8)
        srtSizer.Add(titlebox2, 0, wx.ALIGN_CENTER_VERTICAL)
        srtSizer.AddSpacer(5)
        self.BckgrBtn = wx.ToggleButton(self, label='Background', name='background()', size=(90,24))
        self.BckgrBtn.Bind(wx.EVT_TOGGLEBUTTON, self.onBckgrToggle)
        self.ResetBtn = wx.Button(self, label='Reset', name='reset()', size=(60,24))
        self.ResetBtn.Bind(wx.EVT_BUTTON, self.onReset)
        box1 = wx.BoxSizer(wx.HORIZONTAL)
        box1.Add(self.BckgrBtn, flag=wx.RIGHT, border=8)
        box1.Add(self.ResetBtn, flag=wx.RIGHT, border=8)
        srtSizer.Add(box1, flag=wx.ALIGN_CENTER_VERTICAL)
        #play, pause, save
        self.PlayBtn=wx.Button(self, name='start()')
        bmp1 = wx.Bitmap(os.path.join(build,'play.png'), wx.BITMAP_TYPE_ANY) # create wx.Bitmap object
        self.PlayBtn.SetBitmap(bmp1)
        self.PlayBtn.Bind(wx.EVT_BUTTON, self.onPlaySpec)
        self.PauseBtn=wx.Button(self, name='pause()')
        bmp2 = wx.Bitmap(os.path.join(build,'pause.png'), wx.BITMAP_TYPE_ANY) # create wx.Bitmap object
        self.PauseBtn.SetBitmap(bmp2)
        self.PauseBtn.Bind(wx.EVT_BUTTON, self.onPauseSpec)
        self.SaveBtn=wx.Button(self, label='Save Data', name='save()')
        self.SaveBtn.Bind(wx.EVT_BUTTON, self.onSaveSpec)
        box3 = wx.BoxSizer(wx.HORIZONTAL)
        box3.Add(self.PlayBtn, flag=wx.RIGHT, border=8)
        box3.Add(self.PauseBtn, flag=wx.RIGHT, border=8)
        box3.Add(self.SaveBtn, flag=wx.RIGHT, border=8)
        srtSizer.Add(box3, flag=wx.ALIGN_CENTER_VERTICAL)
        srtSizer.AddSpacer(5)
        box4=wx.BoxSizer(wx.HORIZONTAL)
        self.text2 = wx.StaticText(self,  wx.ID_ANY, label='Integration time [msec] ')
        self.entry2 = wx.TextCtrl(self, wx.ID_ANY,'0', size=(60, -1))
        self.SetInttBtn = wx.Button( self, label='Set', name='Set()', size=(50,24))
        self.SetInttBtn.Bind(wx.EVT_BUTTON, self.onSetIntt)
        box4.Add(self.text2, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        box4.Add(self.entry2, proportion=1, border=8)
        box4.Add(self.SetInttBtn, flag=wx.RIGHT, border=8)
        srtSizer.Add(box4, flag=wx.ALIGN_CENTER_VERTICAL)
        spacer(srtSizer)
        #Sorting
        boxtop=wx.BoxSizer(wx.HORIZONTAL)
        texttop = wx.StaticText(self,  wx.ID_ANY, label='Peak detection Gate')
        texttop.SetFont(font)
        boxtop.Add(texttop, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        srtSizer.AddSpacer(10)
        srtSizer.Add(boxtop, flag=wx.ALIGN_CENTER_VERTICAL)
        box2=wx.BoxSizer(wx.HORIZONTAL)
        self.entry1 = wx.TextCtrl(self, wx.ID_ANY,'0', size=(60, -1))
        self.text1 = wx.StaticText(self,  wx.ID_ANY, label='min ')
        self.entry11 = wx.TextCtrl(self, wx.ID_ANY,'0', size=(60, -1))
        self.text11 = wx.StaticText(self,  wx.ID_ANY, label='max  [RFU]')
        box2.Add(self.entry1, proportion=1, border=8)
        box2.Add(self.text1, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        box2.Add(self.entry11, proportion=1, border=8)
        box2.Add(self.text11, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        srtSizer.Add(box2, flag=wx.ALIGN_CENTER_VERTICAL)
        box5=wx.BoxSizer(wx.HORIZONTAL)
        self.entry3 = wx.TextCtrl(self, wx.ID_ANY,'0', size=(60, -1))
        self.text3 = wx.StaticText(self,  wx.ID_ANY, label='min ')
        self.entry33 = wx.TextCtrl(self, wx.ID_ANY,'0', size=(60, -1))
        self.text33 = wx.StaticText(self,  wx.ID_ANY, label='max   [nm]')
        box5.Add(self.entry3, proportion=1, border=8)
        box5.Add(self.text3, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        box5.Add(self.entry33, proportion=1, border=8)
        box5.Add(self.text33, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        self.SetGateBtn = wx.Button( self, label='Set', name='Set()', size=(50,24))
        self.SetGateBtn.Bind(wx.EVT_BUTTON, self.onSetGate)
        boxnn = wx.BoxSizer(wx.HORIZONTAL)
        boxnn.Add(self.SetGateBtn, flag=wx.RIGHT, border=8)
        srtSizer.Add(box5, flag=wx.ALIGN_CENTER_VERTICAL)
        srtSizer.Add(boxnn, flag=wx.ALIGN_CENTER_VERTICAL)
        spacer(srtSizer)
        boxmid=wx.BoxSizer(wx.HORIZONTAL)
        textmid = wx.StaticText(self,  wx.ID_ANY, label='Config')
        textmid.SetFont(font)
        boxmid.Add(textmid, flag=wx.ALIGN_CENTER_VERTICAL, border=8)
        srtSizer.Add(boxmid, flag=wx.ALIGN_CENTER_VERTICAL)
        self.text4 = wx.StaticText(self,  wx.ID_ANY, label='Droplet travel time  ')
        self.entry4 = wx.TextCtrl(self, wx.ID_ANY,'0.0', size=(60, -1))
        self.text5 = wx.StaticText(self,  wx.ID_ANY, label='[sec]')
        box6 = wx.BoxSizer(wx.HORIZONTAL)
        box6.Add(self.text4, flag=wx.RIGHT, border=8)
        box6.Add(self.entry4, flag=wx.RIGHT, border=8)
        box6.Add(self.text5, flag=wx.RIGHT, border=8)
        srtSizer.Add(box6, flag=wx.ALIGN_CENTER_VERTICAL)
        self.text7 = wx.StaticText(self,  wx.ID_ANY, label='Pulse Time  ')
        self.entry6 = wx.TextCtrl(self, wx.ID_ANY,'0.0', size=(60, -1))
        self.text8 = wx.StaticText(self,  wx.ID_ANY, label='[sec]')
        box9 = wx.BoxSizer(wx.HORIZONTAL)
        box9.Add(self.text7, flag=wx.RIGHT, border=8)
        box9.Add(self.entry6, flag=wx.RIGHT, border=8)
        box9.Add(self.text8, flag=wx.RIGHT, border=8)
        srtSizer.Add(box9, flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSortBtn = wx.Button( self, label='Set', name='Set()', size=(50,24))
        self.SetSortBtn.Bind(wx.EVT_BUTTON, self.onSetConfig)
        box5 = wx.BoxSizer(wx.HORIZONTAL)
        box5.Add(self.SetSortBtn, flag=wx.RIGHT, border=8)
        srtSizer.Add(box5, flag=wx.ALIGN_CENTER_VERTICAL)
        spacer(srtSizer)
        texttitle = wx.StaticText(self,  wx.ID_ANY, label='Sort and Record Events')
        texttitle.SetFont(font)
        box8 = wx.BoxSizer(wx.HORIZONTAL)
        box8.Add(texttitle, flag=wx.RIGHT, border=8)
        srtSizer.Add(box8, flag=wx.ALIGN_CENTER_VERTICAL)
        self.text6 = wx.StaticText(self,  wx.ID_ANY, label='event #')
        self.entry5 = wx.TextCtrl(self, wx.ID_ANY,'0', size=(60, -1))
        self.checkbox1 = wx.CheckBox(self, wx.ID_ANY, label='continuous')
        self.checkbox1.Bind(wx.EVT_CHECKBOX, self.onCheck1)
        self.checkbox2 = wx.CheckBox(self, wx.ID_ANY, label='save')
        self.checkbox2.Bind(wx.EVT_CHECKBOX, self.onCheck2)
        self.StartSortBtn = wx.ToggleButton(self, label='Start', name='Sort()', size=(90,24))
        self.StartSortBtn.Bind(wx.EVT_TOGGLEBUTTON, self.toggledbutton)
        #self.StartSortBtn.SetBackgroundColour((152,251,152))
        box7 = wx.BoxSizer(wx.HORIZONTAL)
        box7.Add(self.text6, flag=wx.RIGHT, border=8)
        box7.Add(self.entry5, flag=wx.RIGHT, border=8)
        box7.Add(self.checkbox1, flag=wx.RIGHT, border=8)
        box7.Add(self.checkbox2, flag=wx.RIGHT, border=8)
        srtSizer.Add(box7, flag=wx.ALIGN_CENTER_VERTICAL)
        box8 = wx.BoxSizer(wx.HORIZONTAL)
        box8.Add(self.StartSortBtn, flag=wx.RIGHT, border=8)
        srtSizer.Add(box8, flag=wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(srtSizer)
        #self.SetBackgroundColour('#f2dd88')

    def onCheck1(self, event):
        cb = event.GetEventObject() 
        if cb.GetValue():
            self.entry5.Disable()
        else:
            self.entry5.Enable()
            #events    
            nr=int(float(self.entry5.GetValue()))
            f='specsp.setEvents('+str(nr)+')'
            pyperclip.copy(f)
            if self.udpSend != False:
                self.udpSend.Send(f)
        #print cb.GetLabel(),' is clicked', cb.GetValue()
        val = not cb.GetValue()
        s = 'setup.specsp.countevents('+str(int(val))+')'
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)
        
    def onCheck2(self, event):
        cb = event.GetEventObject() 
        val = cb.GetValue()
        s = 'setup.specsp.setAutoSave('+str(val)+')'
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)

    def onStart(self):
        nr=int(float(self.entry5.GetValue()))
        f = 'setup.specsp.setEvents('+str(nr)+')'
        pyperclip.copy(f)
        if self.udpSend != False:
            self.udpSend.Send(f)

        s = 'setup.specsp.start()'
        if self.StartSortBtn.GetLabel() == 'Restart':
            s = 'setup.specsp.play()'
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)

    def onStop(self):
        s = 'setup.specsp.pause()'
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)
            
    def toggledbutton(self, event):
        status=MenuBar.SPEC_status
        if status!= True:
            wx.MessageDialog(self, "Please first start the Spectrometer thread first. Spectrometer > Open", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        else:
            # Active State
            if self.StartSortBtn.GetValue() == True:
                self.onStart()
                self.StartSortBtn.SetLabel('Stop')
                #self.StartSortBtn.SetBackgroundColour((250,128,114))
            # Inactive State
            if self.StartSortBtn.GetValue() == False:
                self.onStop()
                self.StartSortBtn.SetLabel('Restart')
                #self.StartSortBtn.SetBackgroundColour((152,251,152))

    def onSetGate(self, event):
        status=MenuBar.SPEC_status
        if status!= True:
            wx.MessageDialog(self, "Please first start the Spectrometer thread first. Spectrometer > Open", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        else:
            try:
                lowerI=int(float(self.entry1.GetValue()))
                upperI=int(float(self.entry11.GetValue()))
                lowerL=int(float(self.entry3.GetValue()))
                upperL=int(float(self.entry33.GetValue()))
            except:
                wx.MessageDialog(self, "Enter a number", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
            s1 = 'setup.specsp.setGate(%d, %d, %d, %d)'%(lowerI, upperI, lowerL, upperL)
            pyperclip.copy(s1)
            if self.udpSend != False:
                self.udpSend.Send(s1)
                self.udpSend.Send(s2)

    def onSetConfig(self, event):
        status=MenuBar.SPEC_status
        if status!= True:
            wx.MessageDialog(self, "Please first start the Spectrometer thread first. Spectrometer > Open", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        else:
            s1 = self.onSetDropTime()
            s2 = self.onSetOnTime()
            pyperclip.copy(s1)
            if self.udpSend != False:
                self.udpSend.Send(s1)
                self.udpSend.Send(s2)

    def onSetOnTime(self):
        try:
                t=float(self.entry6.GetValue())
        except:
            wx.MessageDialog(self, "Enter a number", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        s= 'setup.specsp.setOnTime('+str(t)+')'
        return s

    def onSetDropTime(self):
        try:
                t=float(self.entry4.GetValue())
        except:
            wx.MessageDialog(self, "Enter a number", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        s= 'setup.specsp.setDropTime('+str(t)+')'
        return s    

    def onSetIntt(self, event):
        status=MenuBar.SPEC_status
        if status!= True:
            wx.MessageDialog(self, "Please first start the Spectrometer thread first. Spectrometer > Open", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        else:
            try:
                t=int(float(self.entry2.GetValue()))
            except:
                wx.MessageDialog(self, "Enter a number", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
            sec=t*1000
            s = 'setup.spec.set_int_time(%d)'%(sec)
            pyperclip.copy(s)
            if self.udpSend != False:
                self.udpSend.Send(s)

    def onReset(self,event):
        #if:
        self.BckgrBtn.Enable()
        self.BckgrBtn.SetValue(False)
        s = 'setup.spec.reset()'
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)

    def onBckgrToggle(self,event):
        status = MenuBar.SPEC_status
        if status!= True:
            wx.MessageDialog(self, "Please first start the Spectrometer thread first. Spectrometer > Open", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        else:
            # Active State
            if self.BckgrBtn.GetValue() == True:
                self.onBckgrSpec()
                obj=event.GetEventObject()
                obj.Disable()
                #self.StartSortBtn.SetLabel('Background')
                
            # Inactive State
            #if self.StartSortBtn.GetValue() == False:
            #    self.StartSortBtn.SetValue(False)

    def onBckgrSpec(self):
        s = 'setup.spec.background()' #setup.spec.have_darkness_correction boolean changes!
        if self.udpSend != False:
            self.udpSend.Send(s)

    def onPlaySpec(self,event):
        status=MenuBar.SPEC_status
        if status!= True:
            wx.MessageDialog(self, "Please first start the Spectrometer thread first. Spectrometer > Open", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        else:
            s = 'setup.spec.play()'
            pyperclip.copy(s)
            if self.udpSend != False:
                self.udpSend.Send(s)

    def onPauseSpec(self,event):
        status=MenuBar.SPEC_status
        if status!= True:
            wx.MessageDialog(self, "Please first start the Spectrometer thread first. Spectrometer > Open", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        else:
            s = 'setup.spec.pause()'
            pyperclip.copy(s)
            if self.udpSend != False:
                self.udpSend.Send(s)

    def onStopSpec(self,event):
        status=MenuBar.SPEC_status
        if status!= True:
            wx.MessageDialog(self, "Please first start the Spectrometer thread first. Spectrometer > Open", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        else:
            s = 'setup.spec.stop()'
            pyperclip.copy(s)
            if self.udpSend != False:
                self.udpSend.Send(s)

    def onSaveSpec(self,event):
        status=MenuBar.SPEC_status
        if status!= True:
            wx.MessageDialog(self, "Please first start the Spectrometer thread first. Spectrometer > Open", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
        else:
            s = 'setup.spec.save()'
            print('Data Saved')
            pyperclip.copy(s)
            if self.udpSend != False:
                self.udpSend.Send(s)

class MenuBar(wx.MenuBar):
    """Create the menu bar."""
    #class vars
    PID_status = False
    SPEC_status = False
    #instance vars
    def __init__(self, pumpnrs, tviewer, sviewer, cviewer, udpSend, specpanel): #, pidpanel
        wx.MenuBar.__init__(self)
        self.pumpnrs = pumpnrs
        self.udpSend = udpSend
        self.tvwr = tviewer
        self.svwr = sviewer
        self.cvwr = cviewer
        self.specpanel = specpanel
        #self.pidpanel = pidpanel
        #
        Pumpnrs=list(range(self.pumpnrs))
        fileMenu = wx.Menu()
        self.fileItem1 = fileMenu.Append(wx.ID_EXIT,'Quit')
        self.fileItem2 = fileMenu.Append(wx.ID_ANY, 'Close all communication', 'Close all threads safely. Close()')
        self.Append(fileMenu, 'File')
        arduMenu = wx.Menu()
        self.arduItem1 = arduMenu.Append(wx.ID_ANY,'Open Port', 'Open connection with Arduino. openPort()')
        self.arduItem2 = arduMenu.Append(wx.ID_ANY, 'Close Port', 'Close connection with Arduino. closePort()')
        self.arduItem3 = arduMenu.Append(wx.ID_ANY, 'Open ChipViewer', 'Opening wxChipViewer')
        self.Append(arduMenu, 'Electrode Stack')
        nemMenu = wx.Menu()
        self.nemItem1 = nemMenu.Append(wx.ID_ANY, 'Open NeMESYS bus', 'Open connection with Nemesys. nem.bus_open()')
        self.nemItem2 = nemMenu.Append(wx.ID_ANY, 'Close NeMESYS bus', 'Close connection with Nemesys. nem.bus_close()')
        stopMenu = wx.Menu()
        self.stopAll = stopMenu.Append(wx.ID_ANY, 'Stop All', 'Stop all pumps.')
        self.stopItem=[]
        for i in Pumpnrs:
            self.stopItem.append(stopMenu.Append(wx.ID_ANY, str(i), str(i)))
        nemMenu.Append(wx.ID_ANY, 'Stop Pumps', stopMenu)
        calibrateMenu = wx.Menu()
        self.calibrateItem=[]
        for i in Pumpnrs:
            self.calibrateItem.append(calibrateMenu.Append(wx.ID_ANY, str(i), str(i)))
        nemMenu.Append(wx.ID_ANY, 'Calibrate', calibrateMenu)
        self.Append(nemMenu, 'Nemesys')
        '''
        #IncubationPanel
        pidMenu = wx.Menu()
        self.pidItem1 = pidMenu.Append(wx.ID_ANY, 'Open PID', 'Start PID thread. Pid.start()')
        self.pidItem2 = pidMenu.Append(wx.ID_ANY, 'Pause PID', 'Pause PID thread. Pid.pause()')
        self.pidItem3 = pidMenu.Append(wx.ID_ANY, 'Close PID', 'Stop PID thread. Pid.stop()')
        self.pidItem4 = pidMenu.Append(wx.ID_ANY, 'View Live Temperature Plot', 'Start wxChipViewer')
        self.Append(pidMenu, 'Droplet Incubation')
        '''
        #sortingpanel
        specMenu = wx.Menu()
        self.specItem1 = specMenu.Append(wx.ID_ANY, 'Open Spec', 'Start SPEC thread. Spec.start()')
        self.specItem2 = specMenu.Append(wx.ID_ANY, 'Close Spec', 'Stop SPEC thread. Spec.stop()')
        self.specItem3 = specMenu.Append(wx.ID_ANY, 'View Live Spectrum', 'Start wxSpecViewer')
        self.Append(specMenu, 'Droplet Sorting')

    def onQuit(self,event):
        self.Close()

    def onCloseAll(self,event):
        s= 'close()'
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)

    def onCloseNem(self,event): ### TO EDIT ###
        s= 'Pumps.bus.close()'
        #self.setup.pumpsObjList[pumpID]
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)
        for pump in range(2):
            f= str(setup.pumpsObjList[pump].stop_pumping())
            pyperclip.copy(f)
            if self.udpSend != False:
                self.udpSend.Send(f)

    def onOpenNem(self,event):
        s= 'Pumps.bus.open()'
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)

    def onStopOnePump(self,event):
        item = self.FindItemById(event.GetId())
        s = 'Pumps.pump_stop(setup.nem.pumpID(%s))' %(str(item.GetText()))
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)

    def onStopPumps(self,event):
        s= 'Pumps.pump_stop_all()'
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)

    def onCalibratePump(self,event):
        item = self.FindItemById(event.GetId()) 
        s = 'Pumps.pump_calibration(setup.nem.pumpID(%s))' %(str(item.GetText()))
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

    def onChipVwr(self, event):
        cmd = [str(self.cvwr)]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def onPIDstart(self, event):
        MenuBar.PID_status = True
        #self.PID=True
        #Enable PID sizer
        self.pidpanel.Enable()
        s = 'setup.Pid.start()'
        pyperclip.copy(s)
        if self.udpSend != False:
                self.udpSend.Send(s)

    def onPIDpause(self, event):
        s = 'setup.Pid.pause()'
        pyperclip.copy(s)
        if self.udpSend != False:
                self.udpSend.Send(s)

    def onPIDstop(self, event):
        MenuBar.PID_status = False
        #self.PID = False
        #Disable PID sizer
        self.pidpanel.Disable()
        s = 'setup.Pid.stop()'
        pyperclip.copy(s)
        if self.udpSend != False:
                self.udpSend.Send(s)

    def onPIDVwr(self,event):
        #cmd = [str(self.tvwr)]
        #dir='"E:/Kenza Folder/PYTHON/fungalmicrofluidics/wxTempViewer_fungalmicrofluidics.bat"'
        #os.system(dir)
        print('Opening:'+ cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        """
        s = 'setup.PID.plot()'
        pyperclip.copy(s)
        if self.udpSend != False:
            self.udpSend.Send(s)
        """

    def onStartSpec(self, event):
        MenuBar.SPEC_status = True
        #self.SPEC = True
        #Enable Spec sizer
        self.specpanel.Enable()
        s = 'setup.spec.start()'
        pyperclip.copy(s)
        if self.udpSend != False:
                self.udpSend.Send(s)

    def onStopSpec(self, event):
        #disable sizer
        #self.SPEC = False
        MenuBar.SPEC_status = False
        self.specpanel.Disable()
        s = 'setup.spec.stop()'
        pyperclip.copy(s)
        if self.udpSend != False:
                self.udpSend.Send(s)

    def onSpecVwr(self, event):
        cmd = str(self.svwr)
        print('Opening:'+ cmd)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def SPEC_status(self):
        """check spec status"""
        #return self.SPEC
        return MenuBar.SPEC_status

    def PID_status(self): #(self, menubar) when placed in mainframe
        """checkPID status"""
        #return self.PID   #menubar.PID
        return MenuBar.PID_status

if __name__ == '__main__':
    def fileChooser():
        root = Tkinter.Tk()
        root.withdraw()
        filename = tkFileDialog.askopenfilename(title = 'GUI Fungal uFluidics: Select ArduBridge Protocol file', filetypes = (('python files','*.py'),('all files','*.*')))
        return filename

    def getProgramFolder():
        moduleFile = __file__
        moduleDir = os.path.split(os.path.abspath(moduleFile))[0]
        programFolder = os.path.abspath(moduleDir)
        return programFolder

    buildPath = os.path.join(getProgramFolder(), "build")

    ver = '3.1.2'
    date = time.strftime("%Y-%m-%d %H:%M")
    print 'GUI: Protocol GUI Ver:%s'%(ver)
    print'Now:%s'%(date)
    print 'Copyright: Kenza Samlali, 2020'
    #Command line option parser
    parser = OptionParser()
    parser.add_option('-p', '--protocol', dest='prot', help='TBD', type='string', default='E:/KENZA Folder/PYTHON/fungalmicrofluidics/fungalmicrofluidics/user_config/protocol_KS_clr_sort_nem5_v2.py')
    parser.add_option('-c', '--port', dest='port', help='Remote port to send the commands', type='int', default=7010)
    parser.add_option('-i', '--ip', dest='ip', help='Remote ip (UDP client) to send the commands', type='string', default='127.0.0.1')
    parser.add_option('-v', '--imgvwr', dest='ivwr', help='imgViewer path', type='string', default='E:/Kenza Folder/PYTHON/mimic/mimic/GUI_mimic.bat')

    (options, args) = parser.parse_args()
    path = os.path.split(options.prot)
    #file chooser opens if no other file was specified in the additional text file
    if path[1] == 'Demoprotocol':
        print 'Loading protocol specified file chooser.'
        newPath = fileChooser()
        path = os.path.split(newPath)
    else:
        print 'Loading protocol specified in accompanying address file.'
    #parser resumes
    lib = str(path[1])[:-3]
    path = path[0]
    sys.path.append(path)
    #lib = options.prot
    print 'Importing: %s'%(lib)
    print 'Using remote-ip:port -> %s:%d'%(options.ip, options.port)
    try:
        protocol = __import__(lib)
    except:
        print 'File not found. Loading protocol from file chooser.'
        newPath = fileChooser()
        path = os.path.split(newPath)
        lib = str(path[1])[:-3]
        path = path[0]
        sys.path.append(path)
        protocol = __import__(lib)
    setup = protocol.Setup(ExtGpio=False, gpio=False, chipViewer=False, Pumps=False, Spec=False, SpecSP=False, PID=False, ImgA=False)
    #setup.enOut(True)
    app = wx.App(False)
    #frame =wx.Frame()
    #panel= MainFrame(frame)
    """Main frame"""
    frame = MainFrame(setup, imgViewer=options.ivwr, path=buildPath, ip=options.ip, port=options.port)
    frame.Centre()
    """Splash screen"""
    bitmap = wx.Bitmap(os.path.join(buildPath,'GUI-splash-01.bmp'))
    splash = wx.adv.SplashScreen(
                    bitmap, 
                    wx.adv.SPLASH_CENTER_ON_SCREEN|wx.adv.SPLASH_TIMEOUT, 2000, frame)
    """Show """
    splash.Show()
    time.sleep(4)
    frame.Show()
    #inspection tool for GUI troubleshooting
    #wx.lib.inspection.InspectionTool().Show()
    #
    app.MainLoop()

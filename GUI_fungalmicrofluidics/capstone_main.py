from GSOF_ArduBridge import UDP_Send
import wx
import pyperclip
import Tkinter
from optparse import OptionParser

class imagingGUI():
    '''Init Main class.'''
    def __init__(self, setup, port=-1, ip='127.0.0.1', columns=2):
         '''setup UDP sending protocol for ArduBridge Shell.'''
        udpSend = False
        if port > 1:
            self.udpSend = UDP_Send.udpSend(nameID='', DesIP=ip, DesPort=port)
        self.setup=setup

    def onTrigger(self, event):
        print('Trigger received. Stopping incubation, starting sorting process.')
        if:
            wx.MessageDialog(self, "Trigger!! Incubation will be stopped", "Warning!", wx.OK | wx.ICON_WARNING).ShowModal()
            s = 'setup.ImgTrigger()'
            pyperclip.copy(s)
            if self.udpSend != False:
                self.udpSend.Send(s)

if __name__ == "GUI_KS_Nemesys.GUI_KS_SC_nemesys" or "__main__":
    ver = '1.0'
    print 'Now: %s'%(time.strftime("%Y-%m-%d %H:%M"))
    print 'GUI: Protocol GUI Ver:%s'%(ver)
    print 'Copyright: ...'
    #Command line option parser
    parser = OptionParser()
    parser.add_option('-p', '--protocol', dest='prot', help='TBD', type='string', default='Demoprotocol')
    parser.add_option('-c', '--port', dest='port', help='Remote port to send the commands', type='int', default=7010)
    parser.add_option('-i', '--ip', dest='ip', help='Remote ip (UDP client) to send the commands', type='string', default='127.0.0.1')
    (options, args) = parser.parse_args()
    path = os.path.split(options.prot)
    lib = str(path[1])[:-3]
    path = path[0]
    sys.path.append(path)
    #lib = options.prot
    print 'Importing: %s'%(lib)
    print 'Using remote-ip:port -> %s:%d'%(options.ip, options.port)
    protocol = __import__(lib)
    setup = protocol.Setup(ExtGpio=False, gpio=False, chipViewer=False, Pumps=False, Spec=False, SpecSP=False, PID=False)
    app = wx.App(False)
    frame = imagingGUI(setup, ip=options.ip, port=options.port)
    frame.Show()
    app.MainLoop()
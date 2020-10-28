from GSOF_ArduBridge import threadBasic as TB

class thermalPoint():
    def __init__(self, setPoint=25, timeDuration=1, RC=0.5):
        self.setPoint = setPoint
        self.timeDuration = timeDuration
        self.RC = RC
        
class thermoCycler(TB.BasicThread):
    def __init__(self, name = 'thermalCycler', period=1, pid=False, pntList=[],sideChain=False,sideChainTempChange=False):
        TB.BasicThread.__init__(self, nameID=name, Period = period)
        
        self.pPID = pid
        self.cfg( pntList )
        self.idx = 0
        self.timer = 0
        #self.states = ['IDLE', 'TRNS', 'STBL', 'END']
        self.state = 'IDLE'
        self.sideChain = sideChain
        self.sideChainTempChange = sideChainTempChange

        
    def cfg( self, pntList ):
        self.pntList = pntList

    def start(self):
        self.pPID.start()
        self.idx = 0
        self.timer = 0
        self.state = 'STBL'
        TB.BasicThread.start(self)
                
    def stop(self):
        self.pPID.stop()
        TB.BasicThread.stop(self)

#    def heatshock( self, pnt=(4, 30), pnt2=(42, 20), N=1 ):
    def process( self ):
        state = self.state
        if state == 'IDLE':
            #self.pause()
            self.pPID.pause()

        elif state == 'NEW':
            if self.sideChain != False:
                self.sideChain()
                self.sideChainTempChange = True
            if self.idx < len(self.pntList):
                trg = self.pntList[self.idx].setPoint
                T = self.pntList[self.idx].timeDuration
                TmK = self.pntList[self.idx].RC
                self.idx += 1
                self.pPID.ctrl(trg)
                self.timer = T
                self.pPID.RC_div_DT = (TmK)
                report = '%s Cycle,%d\n'%(self.name, self.idx)
                report += '%s Target, %3.1f[degC] for %3.1f[sec], RC value of: %3.1f[sec]\n'%(self.name, trg, T, TmK)
                self.teleUpdate(report)
                print report
                self.state = 'TRNS'
            else:
                self.state = 'END'

        elif state == 'TRNS':
            if self.pPID.ctrl_Rise > 0:
                self.teleUpdate('%s: Target-Reached')# Waiting, %d[sec]'%(name, waitT)
                self.state = 'STBL'
            
        elif state == 'STBL':
            self.timer += -self.Period
            if self.timer <= 0:
                    self.state = 'NEW'
                    
        elif state == 'END':
            self.teleUpdate('%s: cycle finished\n')
            self.state = 'IDLE'

        else:
            self.teleUpdate('%s: wrong state!!!\n')
            self.state = 'IDLE'


##        cycTemp = [pnt1, pnt2, pnt1]
##        while N>0:
##            print '%s Cycle,%d'%(name, N)
##            for pnt in cycTemp:
##                trg = pnt[0]
##                print '%s Target, %3.1f[degC]'%(name, trg)
##                self.pPID.ctrl(trg)
##                while self.pPID.ctrl_Rise < 0:
##                    time.sleep(1)
##                    
##                waitT = pnt[1]
##                print '%s Target-Reached Waiting, %d[sec]'%(name, waitT)
##                time.sleep(waitT)
##            N -= 1

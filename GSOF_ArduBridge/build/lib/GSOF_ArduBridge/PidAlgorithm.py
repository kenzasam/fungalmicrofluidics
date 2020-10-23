#!/usr/bin/env python
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

Class to build an Enhanced-PID-Controller function.
The controller includes the following fetures:
- Rise-Time and Settle-Time measurements on each command.
- Enhanced antiwindup algorithm for the integrator.
- Configurable integrator limits.
- Configurable output limits.

The NextStep function should be called on periodic bases with new
control, feedback and Ts values.
It returns the new output value.
The class stores its state.
"""

__version__ = "1.0.0"

__author__ = "Guy Soffer"
__copyright__ = "Copyright 2019"
__credits__ = ["James Perry"]
__license__ = "GPL-3.0-or-later"
__maintainer__ = ""
__email__ = "gsoffer@yahoo.com"
__status__ = "Production"

class PidAlgorithm():
    def __init__(self, P, I, D):
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.ctrl = 0
        self.feedback = [0]*3
        self.error = [0]*3
        self.delta = 0
        self.sum = 0
        self.diff = 0
        self.output = 0
        self.outMax = 255
        self.outMin = -255
        self.sumMax = 255
        self.sumMin = -255
        self.cycle = 0

    def NextStep(self, ctrl, feedback, dt):
        if dt < 0.0001:
            print('PID divid by zero! dt is too low')
            return
        self.cycle += 1
        self.ctrl = ctrl
        
        self.feedback.pop(0)              #remove the oldest value
        self.feedback.append(feedback)    #add the newest value

        self.error.pop(0)                 #Remove the oldest value
        self.error.append(ctrl -feedback) #Add the newest value

        self.delta = self.error[-1] * self.Kp

        if (self.Ki == 0):
            self.sum = 0
            dSum = 0
        else:
            dSum = self.error[-1] * self.Ki * dt #Integrate the recent error value
            self.sum += dSum
            if self.sum > self.sumMax:
                self.sum = self.sumMax
            elif self.sum < self.sumMin:
                self.sum = self.sumMin


        #The equation *** Diff(f(x) = (f(x + h) - f(x - h)) / 2h ***
#        self.diff = self.D * (self.error[-1] - self.error[-3]) / 2*dt

        #The equation    *** Diff(f(x) = (f(x) - f(x - h)) / h ***
        self.diff = ((self.error[-1] - self.error[-2])/dt) * self.Kd
        
        self.output = self.delta +self.sum +self.diff

        #Clamp the output results to the limits
        if self.output > self.outMax:
           self.output = self.outMax #Clamp the output to maximum
        elif self.output < self.outMin:
           self.output = self.outMin #Clamp the output to minimum

        #Enhanced-Anti-Windup methode (By: Guy Soffer)
        if ((self.output == self.outMax) or (self.output == self.outMin)):
           if ( (self.sum<0) and (self.output<0) and (dSum<0)
                or
                (self.sum>0) and (self.output>0) and (dSum>0)
                ):
               self.sum -= dSum #Cancel the integration part

        return self.output

    def getStatus(self):
        s = 'Cyc: %d, '%(self.cycle) 
        s +='Ct: %6.1f, Fb: %6.1f, Delta: %6.2f, Sum: %6.2f, Diff: %6.2f, Out: %6.2f'%(self.ctrl,
                                                                                       self.feedback[-1],
                                                                                       self.delta,
                                                                                       self.sum,
                                                                                       self.diff,
                                                                                       self.output)
        return s
        

    def process(self):
        peakfound = False
        try:
            #Find all peaks above noise
            p_int, p_wvl = self.findallpeaks(self.spec.wavelengths, self.spec.data)
            #Filter out peaks outside gates
            wvl_list1 = [i for i in p_wvl if (self.gateL1[0]< i <self.gateL1[1])]
            int_list1 = [i for i in p_int if (self.gateI1[0]< i <self.gateI1[1])]
            wvl_list2 = [i for i in p_wvl if (self.gateI2[0]< i <self.gateI2[1])]
            int_list2 =[i for i in p_wvl if (self.gateL1[0]< i <self.gateL1[1])]
            zz = False
            if len(wvl_list1) >0 or len(wvl_list2) > 0: 
                zz = True # there is at least 1 peak in 1 of the gates
                print('Peak at:'+str(wvl_list1)+str(wvl_list2)) 
            #if len(wvl_list1) > 1 or len(wvl_list2)>1: 
            #    '''Take this conditional statement and resp. exception away to sort even with 
            #    multiple peaks.'''
            #    raise ValueError('WARNING Multiple peaks within gate detected. Correct gate to sort.')
            if len(p_int) > 0 and ( (self.gateL == None) or zz):
                if self.SAVE: 
                    self.savepeaks(filepk, p_wvl, p_int) #saves all peaks, including outside gate
                    #self.savepeaks(filepk, wvl_list, int_list) #saves only peaks within gate 
                if (len(wvl_list1)>0 and len(int_list1)>0):
                    peak1found = True
                if (len(wvl_list2)>0 and len(int_list2)>0):
                    peak2found = True
                if peak1found or peak2found:
                    print('+++')
                    print(str(wvl_list)+'nm, '+str(int_list)+'A.U')
                    if self.countevents(self.peakcnt): 
                        if self.cntr == self.peakcnt:
                            self.lock.release()
                            self.enable = False
                            print('Final event.')
                            end_time = datetime.now()
                            #print('Time elapsed:', end_time - start_time)
                            self.stop()
                        self.cntr += 1
                        print('Peak '+str(self.cntr))
                    if self.electhread and self.enOut:
                        #wait, depending on distance between detection and electrodes
                        time.sleep(self.t_wait)
                        #turn top elec on
                        self.gpio.pinPulse(self.pin_pulse, self.onTime)
                        self.teleUpdate('%s, E%d: %f s pulse'%(self.name, self.pin_pulse, self.onTime))
        except ValueError as e:
            print(e)
        except:
            print('Error...')
            exc_type, exc_value = sys.exc_info()[:2]
            print '%s : Handling %s exception with message "%s"' % \
                (self.name, exc_type.__name__, exc_value)
            #stop thread???
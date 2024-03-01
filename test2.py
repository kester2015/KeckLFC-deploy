
# from Hardware.AmonicsEDFA import AmonicsEDFA
# from Hardware.PritelAmp import  PritelAmp
# from Hardware.InstekGPD_4303S import InstekGPD_4303S
# from Hardware.InstekGppDCSupply import InstekGppDCSupply
# from Hardware.Waveshaper import Waveshaper

# from Hardware.RbClock import RbClock
# from Hardware.PendulumCNT90 import PendulumCNT90
from .Hardware import *
import numpy as np
import time

class KeckLFC(object):
    def __init__(self, 
                amamp_addr = 'ASRL7::INSTR', amamp_name = 'Amonic27 6A 680mW EDFA',
                amamp2_addr = 'ASRL4::INSTR', amamp2_name = 'Amonic 13dbm EDFA',
                ptamp_addr = 'ASRL6::INSTR', ptamp_name = 'Pritel 3.85A 3.6W FA',
                RFoscPS_addr = 'ASRL5::INSTR', RFoscPS_name = 'RF oscillator Power Supply 15V 0.4A',
                RFampPS_addr = 'ASRL34::INSTR', RFampPS_name = 'RF amplifier Power Supply 30V 4.5A',
                rbclock_addr = 'ASRL9::INSTR', rbclock_name = 'FS725 Rubidium Frequency Standard',
                wsp_addr = 'SN201904', wsp_name = "WS1"
                ) -> None:
        self.amamp = AmonicsEDFA(addr=amamp_addr, name = amamp_name)
        self.amamp2 = AmonicsEDFA(addr=amamp2_addr, name = amamp2_name)
        self.ptamp = PritelAmp(addr=ptamp_addr, name=ptamp_name)
        self.RFoscPS = InstekGPD_4303S(addr=RFoscPS_addr, name=RFoscPS_name)
        self.RFampPS = InstekGppDCSupply(addr=RFampPS_addr, name=RFampPS_name)
        self.rbclock = RbClock(addr=rbclock_addr, name=rbclock_name)

        self._dev_list = [self.amamp,self.amamp2, self.ptamp, self.RFampPS, self.RFoscPS, self.rbclock]
        #self._dev_list = [self.amamp,self.amamp2, self.RFampPS, self.RFoscPS]
        

        try:
            self.wsp = Waveshaper(addr=wsp_addr, WSname=wsp_name)
            self._dev_list.append(self.wsp)
        except:
            print("Waveshaper Init Failed.")
            import sys
            e = sys.exc_info()[0]
            print(f"Error:{e}")


    def connect_all(self):
        for device in self._dev_list:
            try:
                device.connect()
            except:
                import sys
                e = sys.exc_info()[0]
                print(f"Error:{e}")

    def printStatus_all(self):
        for device in self._dev_list:
            try:
                device.printStatus()
            except:
                import sys
                e = sys.exc_info()[0]
                print(f"Error:{e}")

    def minicomb_Up(self, amonic_mode = 'APC'):
        print("Mini-Comb Turn UP process Begins".center(80,'-'))

        self.RFoscPS.Vset2 = 15
        self.RFoscPS.Iset2 = 3
        self.RFoscPS.activation = 1
        rfoscPS_out = np.array([0.,0.,0.])
        while not (np.mean(rfoscPS_out)>0.3 and np.mean(rfoscPS_out)<0.5):
            print(f"Waiting RF oscillator Power Supply output stablize to 0.3~0.45A. Last 3 seconds ave = {np.mean(rfoscPS_out)} A....")
            time.sleep(1)
            rfoscPS_out[0] = self.RFoscPS.Iout2
            time.sleep(1)
            rfoscPS_out[1] = self.RFoscPS.Iout2
            time.sleep(1)
            rfoscPS_out[2] = self.RFoscPS.Iout2
            print(rfoscPS_out)

        self.RFampPS.Vset1 = 30
        self.RFampPS.Iset1 = 5
        self.RFampPS.activation1 = 1
        rfampPS_out = np.array([0.,0.,0.])
        while not (np.mean(rfampPS_out)>3 and np.mean(rfampPS_out)<5):
            print(f"Waiting RF oscillator Power Supply output stablize to 4.3~4.5A. Last 3 seconds ave = {np.mean(rfampPS_out)} A....")
            time.sleep(1)
            rfampPS_out[0] = self.RFampPS.Iout1
            time.sleep(1)
            rfampPS_out[1] = self.RFampPS.Iout1
            time.sleep(1)
            rfampPS_out[2] = self.RFampPS.Iout1
            print(rfampPS_out)

            


        if amonic_mode.casefold() == 'acc':
            self.amamp.modeCh1 = 'ACC'
            self.amamp.accCh1Cur = '6A'
            self.amamp.accCh1Status = 1
            self.amamp.activation = 1
            amamp_out = np.array([0.,0.,0.])
            while not (np.mean(amamp_out)>665 and np.mean(amamp_out)<710):
                print(f"Waiting Amonic output stablize to 673mW. Last 3 seconds ave = {np.mean(amamp_out)} mW....")
                time.sleep(1)
                amamp_out[0] = self.amamp.outputPowerCh1
                time.sleep(1)
                amamp_out[1] = self.amamp.outputPowerCh1
                time.sleep(1)
                amamp_out[2] = self.amamp.outputPowerCh1
                print(amamp_out)
        elif amonic_mode.casefold() == 'apc':
            self.amamp.modeCh1 = 'APC'
            self.amamp.accCh1Cur = '630mw'
            self.amamp.accCh1Status = 1
            self.amamp.activation = 1
            amamp_out = np.array([0.,0.,0.])
            while not (np.mean(amamp_out)>625 and np.mean(amamp_out)<635):
                print(f"Waiting Amonic output stablize to 630mW. Last 3 seconds ave = {np.mean(amamp_out)} mW....")
                time.sleep(1)
                amamp_out[0] = self.amamp.outputPowerCh1
                time.sleep(1)
                amamp_out[1] = self.amamp.outputPowerCh1
                time.sleep(1)
                amamp_out[2] = self.amamp.outputPowerCh1
                print(amamp_out)
        elif amonic_mode.casefold() == '23ACC':
            self.amamp.modeCh1 = 'ACC'
            self.amamp.accCh1Cur = '380mA'
            self.amamp.accCh1Status = 1
            self.amamp.accCh2Cur = '760mA'
            self.amamp.accCh2Status = 1
            self.amamp.activation = 1
            amamp_out = np.array([0.,0.,0.])
            while not (np.mean(amamp_out)>198 and np.mean(amamp_out)<208):
                print(f"Waiting Amonic output stablize to 630mW. Last 3 seconds ave = {np.mean(amamp_out)} mW....")
                time.sleep(1)
                amamp_out[0] = self.amamp.outputPowerCh1
                time.sleep(1)
                amamp_out[1] = self.amamp.outputPowerCh1
                time.sleep(1)
                amamp_out[2] = self.amamp.outputPowerCh1
                print(amamp_out)
        else:
            raise ValueError("KeckLFC: Minicomb up unknown Amonic mode"+amonic_mode)
            


        # self.RFoscPS.setAllZero()
        

        print("Mini-Comb Turn UP process Finished".center(80,'-'))


    def minicomb_Down(self):
        print("Mini-Comb Turn DOWN process Begins".center(80,'-'))

        self.amamp2.activation = 0
        self.amamp2.accCh1Status = 0
        # self.amamp2.accCh1Cur = 0

        amamp_out = np.array([1.,1.,1.])*self.amamp.outputPowerCh1
        self.amamp.activation = 0
        self.amamp.accCh1Status = 0
        # self.amamp.accCh1Cur = 0
        while not (np.mean(amamp_out)<1):
            print(f"Waiting Amonic output down below 1mW. Last 3 seconds ave = {np.mean(amamp_out)} mW....")
            time.sleep(1)
            amamp_out[0] = self.amamp.outputPowerCh1
            time.sleep(1)
            amamp_out[1] = self.amamp.outputPowerCh1
            time.sleep(1)
            amamp_out[2] = self.amamp.outputPowerCh1
            print(amamp_out)

        rfampPS_out = np.array([1.,1.,1.])*self.RFampPS.Iout1
        self.RFampPS.activation1 = 0
        while not (np.mean(rfampPS_out)<0.01):
            print(f"Waiting RF oscillator Power Supply output Down below 0.01A. Last 3 seconds ave = {np.mean(rfampPS_out)} A....")
            time.sleep(1)
            rfampPS_out[0] = self.RFampPS.Iout1
            time.sleep(1)
            rfampPS_out[1] = self.RFampPS.Iout1
            time.sleep(1)
            rfampPS_out[2] = self.RFampPS.Iout1
            print(rfampPS_out)

        rfoscPS_out = np.array([1.,1.,1.])*self.RFoscPS.Iout2
        self.RFoscPS.activation = 0
        while not (np.mean(rfoscPS_out)<0.01):
            print(f"Waiting RF oscillator Power Supply output Down below 0.01A. Last 3 seconds ave = {np.mean(rfoscPS_out)} A....")
            time.sleep(1)
            rfoscPS_out[0] = self.RFoscPS.Iout2
            time.sleep(1)
            rfoscPS_out[1] = self.RFoscPS.Iout2
            time.sleep(1)
            rfoscPS_out[2] = self.RFoscPS.Iout2
            print(rfoscPS_out)

        print("Mini-Comb Turn DOWN process Finished".center(80,'-'))

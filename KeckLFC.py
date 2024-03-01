# from Hardware.AmonicsEDFA import AmonicsEDFA
# from Hardware.PritelAmp import  PritelAmp
# from Hardware.InstekGPD_4303S import InstekGPD_4303S
# from Hardware.InstekGppDCSupply import InstekGppDCSupply
# from Hardware.Waveshaper import Waveshaper

# from Hardware.RbClock import RbClock
# from Hardware.PendulumCNT90 import PendulumCNT90
from Hardware import *
import numpy as np
import time


class EquipmentManager(object):

    def __init__(self) -> None:
        self.equipment_list = []

        self.osa = Agilent_86142B(addr='GPIB0::30::INSTR', name='Agilent 86142B Optical Spectrum Analyzer')

        self.amonics_13 = AmonicsEDFA(addr='ASRL4::INSTR', name='Amonic 13dbm EDFA')
        self.amonics_23 = AmonicsEDFA(addr='ASRL13::INSTR', name='Amonic 23dbm EDFA')
        self.amonics_27 = AmonicsEDFA(addr='ASRL7::INSTR', name='Amonic 27dbm EDFA')
        self.pritel = PritelAmp(addr='ASRL6::INSTR', name='Pritel High Power EDFA')
        self.waveshaper = Waveshaper(addr='SN201904', name="WS1")
        self.srsframe = SRS_SIM900(addr='GPIB0::2::INSTR', name='SRS SIM900 mainframe')

        self.dcbias_1 = InstekGPD_4303S(addr='ASRL5::INSTR', name='4 channel DC Bias Supply InstekGPD_4303S')
        self.dcps_1 = InstekGppDCSupply(addr='ASRL10::INSTR', name='1 channel DC Power Supply InstekGpp')
        self.dcps_2 = InstekGppDCSupply(addr='ASRL34::INSTR', name='1 channel DC Power Supply InstekGpp')

        self.rbclock = RbClock(addr='ASRL9::INSTR', name='FS725 Rubidium Frequency Standard')
        self.pendulum = PendulumCNT90(addr='GPIB0::10::INSTR', name='Pendulum CNT90')

        self.fctec = TEC_LFC3751(addr='ASRL41::INSTR', name='Filter cavity TEC LFC3751')

        self.rio = ORIONLaser(addr='ASRL8::INSTR', name='Rio ORION Laser')

    # def add_equipment(self, varname:str, device):
    #     '''
    #     Add equipment to manage
    #     ===
    #     Inputs:
    #     ====
    #         varname: string will be converted to attribute name.
    #         device: object that is a Device class (Device class defined in Hardware.Device)
    #     '''
    #     if hasattr(self, varname):
    #         raise ValueError("EquipmentManager: attribute name "+varname+" already exists. Change varname then try Add equipment again.")

    #     setattr(self,varname,device)
    #     self.equipment_list.append(getattr(self,varname))

    # def get_addressbook(self):
    #     self.addressbook = {'amamp27':["ASRL7::INSTR"],
    #                         'amamp13':["ASRL4::INSTR"],
    #                         'amamp23':["ASRL13::INSTR"],
    #                         }


''' Some test functions for KTL implementation'''

import xml.etree.ElementTree as ET
import threading


def parse_xml(xmlfile):
    tree = ET.parse(xmlfile)
    root = tree.getroot()

    keyword_names = []
    keyword_types = []

    for keyword in root.findall('keyword'):
        name = keyword.find('name').text
        keyword_type = keyword.find('type').text
        #capability_type = keyword.find('capability').get('type')

        print('Parsed keyword: name=%s\ttype=%s' % (name, keyword_type))
        keyword_names.append(name)
        keyword_types.append(keyword_type)

    return keyword_names, keyword_types

def KTLarray(values):
    ''' converts list to an array that KTL can recognize'''
    return " ".join(map(str, values)) 

def test_clock(stop, mkl):
    while True:
        mkl.keywords['ICECLK'] = time.strftime('%H:%M:%S')
        time.sleep(1)
        if stop():
            mkl.clock = None
            break


class KeckLFC(object):

    def __init__(self,
                 amamp_addr='ASRL13::INSTR',
                 amamp_name='Amonic 6A 680mW EDFA',
                 amamp2_addr='ASRL4::INSTR',
                 amamp2_name='Amonic 13dbm EDFA',
                 ptamp_addr='ASRL6::INSTR',
                 ptamp_name='Pritel 3.85A 3.6W FA',
                 RFoscPS_addr='ASRL5::INSTR',
                 RFoscPS_name='RF oscillator Power Supply 15V 0.4A',
                 RFampPS_addr='ASRL10::INSTR',
                 RFampPS_name='RF amplifier Power Supply 30V 4.5A',
                 rbclock_addr='ASRL9::INSTR',
                 rbclock_name='FS725 Rubidium Frequency Standard',
                 wsp_addr='SN201904',
                 wsp_name="WS1") -> None:
        if False:
            self.amamp = AmonicsEDFA(addr=amamp_addr, name=amamp_name)
            self.amamp2 = AmonicsEDFA(addr=amamp2_addr, name=amamp2_name)
            self.ptamp = PritelAmp(addr=ptamp_addr, name=ptamp_name)
            self.RFoscPS = InstekGPD_4303S(addr=RFoscPS_addr, name=RFoscPS_name)
            self.RFampPS = InstekGppDCSupply(addr=RFampPS_addr, name=RFampPS_name)
            self.rbclock = RbClock(addr=rbclock_addr, name=rbclock_name)

            self._dev_list = [self.amamp, self.amamp2, self.ptamp, self.RFampPS, self.RFoscPS, self.rbclock]
        '''
        self.osa = AndoOSA_AQ6315E(addr='GPIB1::1::INSTR', name='Ando AQ6317B OSA')

        try:
            self.wsp = Waveshaper(addr=wsp_addr, WSname=wsp_name)
            self._dev_list.append(self.wsp)
        except:
            print("Waveshaper Init Failed.")
            import sys
            e = sys.exc_info()[0]
            print(f"Error:{e}")
        '''

        ''' KTL keywords'''
        keyword_names, keyword_types = parse_xml(r"LFC.xml.sin")

        self.keywords = {keyword: None for keyword in keyword_names}
        self.types = {keyword: keyword_type for keyword, keyword_type in zip(keyword_names, keyword_types)}

        func_dict = {}
        for keyword in self.keywords:
            method_name = f'{keyword}'
            method = getattr(self, method_name)
            func_dict[keyword] = method

        self.funcs = func_dict

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

    def minicomb_Up(self, amonic_mode='23ACC'):
        print("Mini-Comb Turn UP process Begins".center(80, '-'))
        if amonic_mode.casefold() == 'acc':
            self.amamp.modeCh1 = 'ACC'
            self.amamp.accCh1Cur = '6A'
            self.amamp.accCh1Status = 1
            self.amamp.activation = 1
            amamp_out = np.array([0., 0., 0.])
            while not (np.mean(amamp_out) > 665 and np.mean(amamp_out) < 710):
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
            amamp_out = np.array([0., 0., 0.])
            while not (np.mean(amamp_out) > 625 and np.mean(amamp_out) < 635):
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
            amamp_out = np.array([0., 0., 0.])
            while not (np.mean(amamp_out) > 198 and np.mean(amamp_out) < 208):
                print(f"Waiting Amonic output stablize to 630mW. Last 3 seconds ave = {np.mean(amamp_out)} mW....")
                time.sleep(1)
                amamp_out[0] = self.amamp.outputPowerCh1
                time.sleep(1)
                amamp_out[1] = self.amamp.outputPowerCh1
                time.sleep(1)
                amamp_out[2] = self.amamp.outputPowerCh1
                print(amamp_out)
        else:
            raise ValueError("KeckLFC: Minicomb up unknown Amonic mode" + amonic_mode)

        # self.RFoscPS.setAllZero()
        self.RFoscPS.Vset2 = 15
        self.RFoscPS.Iset2 = 3
        self.RFoscPS.activation = 1
        rfoscPS_out = np.array([0., 0., 0.])
        while not (np.mean(rfoscPS_out) > 0.3 and np.mean(rfoscPS_out) < 0.45):
            print(
                f"Waiting RF oscillator Power Supply output stablize to 0.3~0.45A. Last 3 seconds ave = {np.mean(rfoscPS_out)} A...."
            )
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
        rfampPS_out = np.array([0., 0., 0.])
        while not (np.mean(rfampPS_out) > 4.3 and np.mean(rfampPS_out) < 4.5):
            print(
                f"Waiting RF oscillator Power Supply output stablize to 4.3~4.5A. Last 3 seconds ave = {np.mean(rfampPS_out)} A...."
            )
            time.sleep(1)
            rfampPS_out[0] = self.RFampPS.Iout1
            time.sleep(1)
            rfampPS_out[1] = self.RFampPS.Iout1
            time.sleep(1)
            rfampPS_out[2] = self.RFampPS.Iout1
            print(rfampPS_out)

        print("Mini-Comb Turn UP process Finished".center(80, '-'))

    def minicomb_Down(self):
        print("Mini-Comb Turn DOWN process Begins".center(80, '-'))

        self.amamp2.activation = 0
        self.amamp2.accCh1Status = 0
        # self.amamp2.accCh1Cur = 0

        amamp_out = np.array([1., 1., 1.]) * self.amamp.outputPowerCh1
        self.amamp.activation = 0
        self.amamp.accCh1Status = 0
        # self.amamp.accCh1Cur = 0
        while not (np.mean(amamp_out) < 1):
            print(f"Waiting Amonic output down below 1mW. Last 3 seconds ave = {np.mean(amamp_out)} mW....")
            time.sleep(1)
            amamp_out[0] = self.amamp.outputPowerCh1
            time.sleep(1)
            amamp_out[1] = self.amamp.outputPowerCh1
            time.sleep(1)
            amamp_out[2] = self.amamp.outputPowerCh1
            print(amamp_out)

        rfampPS_out = np.array([1., 1., 1.]) * self.RFampPS.Iout1
        self.RFampPS.activation1 = 0
        while not (np.mean(rfampPS_out) < 0.01):
            print(
                f"Waiting RF oscillator Power Supply output Down below 0.01A. Last 3 seconds ave = {np.mean(rfampPS_out)} A...."
            )
            time.sleep(1)
            rfampPS_out[0] = self.RFampPS.Iout1
            time.sleep(1)
            rfampPS_out[1] = self.RFampPS.Iout1
            time.sleep(1)
            rfampPS_out[2] = self.RFampPS.Iout1
            print(rfampPS_out)

        rfoscPS_out = np.array([1., 1., 1.]) * self.RFoscPS.Iout2
        self.RFoscPS.activation = 0
        while not (np.mean(rfoscPS_out) < 0.01):
            print(
                f"Waiting RF oscillator Power Supply output Down below 0.01A. Last 3 seconds ave = {np.mean(rfoscPS_out)} A...."
            )
            time.sleep(1)
            rfoscPS_out[0] = self.RFoscPS.Iout2
            time.sleep(1)
            rfoscPS_out[1] = self.RFoscPS.Iout2
            time.sleep(1)
            rfoscPS_out[2] = self.RFoscPS.Iout2
            print(rfoscPS_out)

        print("Mini-Comb Turn DOWN process Finished".center(80, '-'))

    ########## Above are deprecated functions ##########

    ########## Below are new functions, will be needed for KTL. ##########

    def __getitem__(self, key):
        '''Read keywords. 
        Calls the associated function, stores the returned value. 
        This is called periodically.'''
        val = self.funcs[key](value=None)

        if val != None: 
            # Store the keyword value in keywords dictionary
            self.keywords[key] = val
        
            return val
    
    def __setitem__(self, key, val):
        '''Write keywords.
        When keyword values are changed by KTL user, stores the value.'''
        if val != None: val = self.convert_type(self.types[key], val)
        
        status = self.funcs[key](value = val)

        # if successful, store the keyword value
        if status == 0: self.keywords[key] = val
        elif status == -1: 
            # actually this is never called because writing a keyword value 
            # to a non-writable keyword is already blocked by KTL
            print('This is non-writable keyword')


        else: 
            print('Error detected in writing ', val, 'to ', key)
            print('status:', status, type(status))
    
    @staticmethod
    def convert_type(typ, val):
        
        if typ == 'integer': return int(val)
        elif typ == 'double': return float(val)
        elif typ == 'enumerated': return int(val)
        elif typ == 'string': return str(val)
        elif typ == 'boolean': 
            if val in ['True', '1', 1, True] : return True
            else: return False
        elif typ =='double array': 
            values = val.strip("()").split(",")
            return [float(value) for value in values]
        else:
            print('Unrecognized type')
            raise Exception
        
    # KTL keywords Implementation

    ########## KTL Keywords Implementation ############

    def LFC_TEMP_TEST1(self, value=None):
        # return
        if value == None:
            from Hardware.USB2408 import USB2408
            daq1 = USB2408(addr=0)
            daq1.connect()    
            temp1 = daq1.get_temp_all()
            # print(temp1)
            daq1.disconnect()
            return KTLarray(temp1)
        else:
            return 0

    def LFC_TEMP_TEST2(self, value=None):
        # return
        if value == None:
            from Hardware.USB2408 import USB2408
            daq1 = USB2408(addr=1)
            daq1.connect()    
            temp1 = daq1.get_temp_all()
            # print(temp1)
            daq1.disconnect()
            return KTLarray(temp1)
        else:
            return 0

    def LFC_T_GLY_RACK_IN(self, value=None):
        return
        if value == None:
            addr = 0
            chan = 5
            from Hardware.USB2408 import USB2408
            daq = USB2408(addr=addr)
            daq.connect()
            temp = daq.get_temp(chan)
            daq.disconnect()
            return temp
        else:
            return 0
        
    def LFC_T_GLY_RACK_OUT(self, value=None):
        return
        if value == None:
            addr = 0
            chan = 4
            from Hardware.USB2408 import USB2408
            daq = USB2408(addr=addr)
            daq.connect()
            temp = daq.get_temp(chan)
            daq.disconnect()
            return temp
        else:
            raise ValueError("LFC_T_GLY_RACK_OUT is read-only")
            return
        
    def LFC_T_EOCB_IN(self, value=None):
        return
        if value == None:
            addr = 1
            chan = 5
            from Hardware.USB2408 import USB2408
            daq = USB2408(addr=addr)
            daq.connect()
            temp = daq.get_temp(chan)
            daq.disconnect()
            return temp
        else:
            raise ValueError("LFC_T_EOCB_IN is read-only")
            return

    def LFC_T_EOCB_OUT(self, value=None):
        return
        if value == None:
            addr = 1
            chan = 4
            from Hardware.USB2408 import USB2408
            daq = USB2408(addr=addr)
            daq.connect()
            temp = daq.get_temp(chan)
            daq.disconnect()
            return temp
        else:
            raise ValueError("LFC_T_EOCB_OUT is read-only")
            return
        
    def LFC_T_RACK_TOP(self, value=None):
        return
        if value == None:
            addr = 0
            chan = 3 # Use Pritel Amplifier TEC as the rack top temperature
            from Hardware.USB2408 import USB2408
            daq = USB2408(addr=addr)
            daq.connect()
            temp = daq.get_temp(chan)
            daq.disconnect()
            return temp
        else:
            raise ValueError("LFC_T_RACK_TOP is read-only")
            return
        
    def LFC_T_RACK_MID(self, value=None):
        return
        if value == None:
            addr = 0
            chan = 0 # Use Side buffle as the rack mid temperature
            from Hardware.USB2408 import USB2408
            daq = USB2408(addr=addr)
            daq.connect()
            temp = daq.get_temp(chan)
            daq.disconnect()
            return temp
        else:
            raise ValueError("LFC_T_RACK_MID is read-only")
            return
    
    def LFC_T_RACK_BOT(self, value=None):
        return
        if value == None:
            addr = 0
            chan = 6 # Bottom rack temperature
            from Hardware.USB2408 import USB2408
            daq = USB2408(addr=addr)
            daq.connect()
            temp = daq.get_temp(chan)
            daq.disconnect()
            return temp
        else:
            raise ValueError("LFC_T_RACK_BOT is read-only")
            return




    def LFC_RIO_T(self, value=None):

        if value == None:
            addr = 0
            chan = 6 # Bottom rack temperature  need recheck
            from Hardware.USB2408 import USB2408
            daq = USB2408(addr=addr)
            daq.connect()
            temp = daq.get_temp(chan)
            daq.disconnect()
            return temp
        else:
            raise ValueError("LFC_T_RACK_BOT is read-only")
            return
        # ==============================
        # if value == None:
        #     # This is called periodically
        #     # Insert some function to execute when this keyword is being read and return the value
        #     # If you don't want the KeckLFC class to modify this keyword, no need to return a value
        #     return

        # else:
        #     # This is called when user modifies the keyword
        #     # Insert some function to execute when user modifies this keyword
        #     # If it's successful, return 0
        #     return 0  # return

    def LFC_RIO_I(self, value=None):
        from KeckLFC.Hardware.ORIONLaser import ORIONLaser
        rio = ORIONLaser(addr=f'ASRL{14}::INSTR')
        rio.connect()

        if value == None:
            
            ii=rio.readLaserdiodeCur_mA()
            print(f'RIO_I: {ii}mA')
            rio.disconnect()
            return ii
            #rio.printStatus()
        else:
            rio.writeLaserdiodeCur_mA(value)
            # need set default
            ii=rio.readLaserdiodeCur_mA()
            return ii

    def LFC_EDFA27_P(self, value=None):
        from KeckLFC.Hardware.AmonicsEDFA import AmonicsEDFA
        amonic27 = AmonicsEDFA(addr=f'ASRL{6}::INSTR', name='Amonics EDFA 27 dBm')
        amonic27.connect()
        if value == None:
            
            edfa27p=amonic27.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic27.disconnect()
            return edfa27p
            #rio.printStatus()
        else:
            amonic27._setChMode('acc')
            amonic27.accCh1Cur=value

            edfa27p=amonic27.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic27.disconnect()
            return edfa27p


    def LFC_EDFA27_ONOFF(self, value=None):

        from KeckLFC.Hardware.AmonicsEDFA import AmonicsEDFA
        amonic27 = AmonicsEDFA(addr=f'ASRL{6}::INSTR', name='Amonics EDFA 27 dBm')
        amonic27.connect()
        if value == None:
            
            edfa27onoff=amonic27.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic27.disconnect()
            return edfa27onoff
            #rio.printStatus()
        else:
            amonic27.accCh1Status=value
            edfa27onoff=amonic27.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic27.disconnect()
            return edfa27onoff

    def LFC_EDFA13_P(self, value=None):
        from KeckLFC.Hardware.AmonicsEDFA import AmonicsEDFA
        amonic13 = AmonicsEDFA(addr=f'ASRL{9}::INSTR', name='Amonics EDFA 13 dBm')
        amonic13.connect()

        if value == None:
            
            edfa27p=amonic13.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic13.disconnect()
            return edfa27p
            #rio.printStatus()
        else:
            amonic13._setChMode('acc')
            amonic13.accCh1Cur=value

            edfa27p=amonic13.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic13.disconnect()
            return edfa27p

    def LFC_EDFA13_ONOFF(self, value=None):
        from KeckLFC.Hardware.AmonicsEDFA import AmonicsEDFA
        amonic13 = AmonicsEDFA(addr=f'ASRL{9}::INSTR', name='Amonics EDFA 13 dBm')
        amonic13.connect()

        if value == None:
            
            edfa27onoff=amonic13.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic13.disconnect()
            return edfa27onoff
            #rio.printStatus()
        else:
            amonic13.accCh1Status=value
            edfa27onoff=amonic13.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic13.disconnect()
            return edfa27onoff

    def LFC_EDFA23_P(self, value=None):
        from KeckLFC.Hardware.AmonicsEDFA import AmonicsEDFA
        amonic23 = AmonicsEDFA(addr=f'ASRL{12}::INSTR', name='Amonics EDFA 23 dBm')
        amonic23.connect()

        if value == None:
            
            edfa27p=amonic23.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic23.disconnect()
            return edfa27p
            #rio.printStatus()
        else:
            amonic23._setChMode('acc')
            amonic23.accCh1Cur=value

            edfa27p=amonic23.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic23.disconnect()
            return edfa27p

    def LFC_EDFA23_ONOFF(self, value=None):
        from KeckLFC.Hardware.AmonicsEDFA import AmonicsEDFA
        amonic23 = AmonicsEDFA(addr=f'ASRL{12}::INSTR', name='Amonics EDFA 23 dBm')
        amonic23.connect()

        if value == None:
            
            edfa27onoff=amonic23.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic23.disconnect()
            return edfa27onoff
            #rio.printStatus()
        else:
            amonic23.accCh1Status=value
            edfa27onoff=amonic23.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic23.disconnect()
            return edfa27onoff

    def LFC_RFAMP_I(self, value=None):
        from KeckLFC.Hardware.InstekGppDCSupply import InstekGppDCSupply
        rfampPS = InstekGppDCSupply(addr=f'ASRL{4}::INSTR', name='RF amplifier PS 30V 4A')
        rfampPS.connect()

        if value == None:
            
            rfampPS_i=rfampPS.Iout1
            print(f'LFC_RFAMP_I : +{rfampPS_i}A')
            rfampPS.disconnect()
            return rfampPS_i
            #rio.printStatus()
        else:
            rfampPS.Iout1=value
            rfampPS_i=rfampPS.Iout1
            print(f'LFC_RFAMP_I : +{rfampPS_i}A')
            rfampPS.disconnect()
            return rfampPS_i
            

    def LFC_RFAMP_V(self, value=None):
        from KeckLFC.Hardware.InstekGppDCSupply import InstekGppDCSupply
        rfampPS = InstekGppDCSupply(addr=f'ASRL{4}::INSTR', name='RF amplifier PS 30V 4A')
        rfampPS.connect()

        if value == None:
            
            rfampPS_i=rfampPS.Vout1
            print(f'LFC_RFAMP_V : +{rfampPS_i}V')
            rfampPS.disconnect()
            return rfampPS_i
            #rio.printStatus()
        else:
            rfampPS.Vout1=value
            rfampPS_i=rfampPS.Vout1
            print(f'LFC_RFAMP_V : +{rfampPS_i}V')
            rfampPS.disconnect()
            return rfampPS_i

    def LFC_RFOSCI_I(self, value=None):
        from KeckLFC.Hardware.InstekGPD_4303S import InstekGPD_4303S
        rfoscPS = InstekGPD_4303S(addr='ASRL13::INSTR', name='RF oscilator PS, CH2 15V, CH3 1V')
        rfoscPS.connect()
        if value == None:
            
            rfoscPS_i=rfoscPS.Iout2
            rfoscPS.disconnect()
            return rfoscPS_i
            
        else:
            rfoscPS.Iset2=value
            rfoscPS_i=rfoscPS.Iout2
            rfoscPS.disconnect()
            return rfoscPS_i

    def LFC_RFOSCI_V(self, value=None):

        from KeckLFC.Hardware.InstekGPD_4303S import InstekGPD_4303S
        rfoscPS = InstekGPD_4303S(addr='ASRL13::INSTR', name='RF oscilator PS, CH2 15V, CH3 1V')
        rfoscPS.connect()
        if value == None:
            
            rfoscPS_i=rfoscPS.Vout2
            rfoscPS.disconnect()
            return rfoscPS_i
            
        else:
            rfoscPS.Vset2=value
            rfoscPS_i=rfoscPS.Vout2
            rfoscPS.disconnect()
            return rfoscPS_i

    def LFC_IM_BIAS(self, value=None):

        from KeckLFC.Hardware.SRS_SIM900 import SRS_SIM900, SRS_PIDcontrol_SIM960
        srs = SRS_SIM900(addr='GPIB0::2::INSTR')
        srs.connect()
        servo_IM = SRS_PIDcontrol_SIM960(srs, 3, name='Minicomb Intensity Lock Servo')
        if value == None:
            
            
            IM_bias=servo_IM.get_output_voltage()

            srs.disconnect()
            return IM_bias

        else:
            servo_IM.manual_output=value

            IM_bias=servo_IM.get_output_voltage()

            srs.disconnect()
            return IM_bias

    def LFC_IM_RF_ATT(self, value=None):

        from KeckLFC.Hardware.InstekGPD_4303S import InstekGPD_4303S
        rfoscPS = InstekGPD_4303S(addr='ASRL13::INSTR', name='RF oscilator PS, CH2 15V, CH3 1V')
        rfoscPS.connect()
        if value == None:
            
            rfoscPS_i=rfoscPS.Vout3
            rfoscPS.disconnect()
            return rfoscPS_i
            
        else:
            rfoscPS.Vset2=value
            rfoscPS_i=rfoscPS.Vout3
            rfoscPS.disconnect()
            return rfoscPS_i

    def LFC_WSP_PHASE(self, value=None):

        if value != None:
            from KeckLFC.Hardware.Waveshaper import Waveshaper
            ws = Waveshaper()
            ws.connect()

            d2 = value
            ws.set3rdDisper(d2,d3=0.)
            ws.disconnect()
            return 1

        else:
            # ws need recheck
            return 0

    def LFC_WSP_ATTEN(self, value=None):
        if value == None:
            # This is called periodically
            # Insert some function to execute when this keyword is being read and return the value
            # If you don't want the KeckLFC class to modify this keyword, no need to return a value
            return

        else:
            # This is called when user modifies the keyword
            # Insert some function to execute when user modifies this keyword
            # If it's successful, return 0
            return 0  # return

    def LFC_PTAMP_PRE_P(self, value=None):
        from KeckLFC.Hardware.PritelAmp import PritelAmp
        ptamp = PritelAmp(addr=f'ASRL{7}::INSTR', name='Pritel Amp')
        ptamp.connect()
        if value != None:

            ptamp.preAmp = f'{value}'+'mA'
            pre_p=ptamp.preAmp
            ptamp.disconnect()
            return pre_p
        else:
            pre_p=ptamp.preAmp
            ptamp.disconnect()
            return pre_p

    def LFC_PTAMP_OUT(self, value=None):
        if value != None:

            from KeckLFC.Hardware.PritelAmp import PritelAmp
            ptamp = PritelAmp(addr=f'ASRL{7}::INSTR', name='Pritel Amp')
            ptamp.connect()

            pre_out=ptamp.outputPwr_mW
            ptamp.disconnect()
            return pre_out
        else:
            raise ValueError("LFC_PTAMP_OUT is read only")
            return

    def LFC_PTAMP_I(self, value=None):

        from KeckLFC.Hardware.PritelAmp import PritelAmp
        ptamp = PritelAmp(addr=f'ASRL{7}::INSTR', name='Pritel Amp')
        ptamp.connect()

        if value != None:

            ptamp.pwrAmp = f'{value}'+'A'
            ptamp.disconnect()
            return 1

        else:
            ptamp=ptamp.pwrAmp
            ptamp.disconnect()
            return ptamp  # return

    def LFC_PTAMP_ONOFF(self, value=None):

        from KeckLFC.Hardware.PritelAmp import PritelAmp
        ptamp = PritelAmp(addr=f'ASRL{7}::INSTR', name='Pritel Amp')
        ptamp.connect()

        if value != None:

            ptamp.activation = value
            ptact = ptamp.activation
            ptamp.disconnect()
            return ptact

        else:
            ptact=ptamp.activation
            ptamp.disconnect()
            return ptact  # return

    def LFC_PTAMP_LATCH(self, value=None):
        if value == None:
            from KeckLFC.Hardware.Arduino_relay import Arduino_relay
            arduino = Arduino_relay(addr=f"COM3")
            # print(f'com={i}')
            arduino.connect()
            return

        else:
            # This is called when user modifies the keyword
            # Insert some function to execute when user modifies this keyword
            # If it's successful, return 0
            return 0  # return

    def LFC_WGD_T(self, value=None):

        from KeckLFC.Hardware.TEC_TC720 import TEC_TC720

        tec_ppln = TEC_TC720(addr=f'COM{22}', name='PPLN Doubler TEC (TC720)')
        tec_ppln.connect()

        if value == None:
            tppln=tec_ppln.get_temp()
            tec_ppln.disconnect()
            return tppln

        else:
            tec_ppln.set_temp(value)
            tppln=tec_ppln.get_temp()
            tec_ppln.disconnect()
            return tppln

    def LFC_PPLN_T(self, value=None):

        from KeckLFC.Hardware.TEC_TC720 import TEC_TC720
        # tec_PPLN = TEC_TC720(addr='ASRL46::INSTR')
        tec_wg = TEC_TC720(addr='COM16', name='Octave Waveguide TEC (TC720)')
        tec_wg.connect()

        if value == None:
            twg=tec_wg.get_temp()
            tec_wg.disconnect()
            return twg

        else:
            tec_wg.set_temp(value)
            twg=tec_wg.get_temp()
            tec_wg.disconnect()
            return twg

    ########## These are just test keywords and functions ############

    def ICECLK_ONOFF(self, value=None):
        '''Turn on / off the clock '''

        if value == None:
            return self.keywords['ICECLK_ONOFF']

        else:
            print('ICECLK value: ', value)
            print('Writing value', value, 'to ICECLK_ONOFF')
            if value == True:
                self.start_clock()
            elif value == False:
                self.stop_clock()
            else:
                print('something wrong with ICECLK_ONOFF')
                return 1
            return 0

    def ICECLK(self, value=None):
        ''' shows current time returned by ice'''

        if value == None:
            return self.keywords['ICECLK']

        else:
            print('Writing value', value, 'to ICECLK')
            return 0

    def ICESTA(self, value=None):
        ''' shows status of the ICE connection'''

        if value == None:
            return  #self.keywords['ICESTA']
        else:
            print('Writing value', value, 'to icesta')
            if value == 2:
                print('ICE - KTL disconnected!')
            return 0

    def start_clock(self):
        self._stop_clock = False
        self.clock = threading.Thread(target=test_clock, args=(lambda: self._stop_clock, self))
        print('\t\t\tstart clock')
        self.clock.start()

    def stop_clock(self):
        print('\t\t\tstop clock')
        self._stop_clock = True
        self.clock.join()

    def SHOW_ALL_VAL(self, value=None):

        if value == None:
            return
        else:

            if value == True:
                print(self.keywords)
                print(value, type(value))
            return 0

    def ICETEST(self, value=None):
        '''When called, randomly returns an integer value between 1 to 10'''
        #print('ICETEST input value', value)
        if value == None:
            # show
            import random
            value_to_return = random.randint(1, 10)
            return value_to_return  #self.keywords['ICETEST']

        else:
            # modify
            #print('modify icetest called')
            return 0
        
    def ICEARRAY(self, value=None):
        '''When called, randomly returns an integer value between 1 to 10'''
        # print('ICEARRAY input value', value)
        if value == None:
            return
            # show
            # value_to_return = []
            # import random
            # value_to_return.append(random.randint(1, 10))
            # value_to_return.append(random.random())
            # print('ICEARRAY setting',(value_to_return))
            # return KTLarray(value_to_return)  #self.keywords['ICETEST']

        else:
            # modify
            #print('modify ICEARRAY called')
            return 0


if __name__ == "__main__":
    lfc = KeckLFC()
    #lfc.osa.connect()
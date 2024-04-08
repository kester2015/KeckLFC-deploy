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

icetest_mode = False


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
        # print('Parsed keyword: name=%s\ttype=%s' % (name, keyword_type))
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

class AddressBook:
    def __init__(self):
        self.ptamp_addr = 'ASRL6::INSTR'
        self.ptamp_name = 'Pritel 3.85A 3.6W FA'
        # TODO: Add more devices

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

        # self.addr_book = {}
        # self.addr_book['ptamp'] = "ASTR"
        # TODO: Aggregrate to AddressBook class
        # address_book = AddressBook()
        

        ''' KTL keywords'''
        if icetest_mode: 
            keyword_names, keyword_types = parse_xml(r"testLFC.xml.sin")
        else:
            keyword_names, keyword_types = parse_xml(r"LFC.xml.sin")

        self.keywords = {keyword: None for keyword in keyword_names}
        self.types = {keyword: keyword_type for keyword, keyword_type in zip(keyword_names, keyword_types)}

        func_dict = {}
        for keyword in self.keywords:
            method_name = f'{keyword}'
            method = getattr(self, method_name)
            func_dict[keyword] = method

        self.funcs = func_dict


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
        return
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
        return
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

    def LFC_T_GLY_EOCB_IN(self, value=None): return
    def LFC_T_GLY_EOCB_OUT(self, value=None): return
    def LFC_T_GLY_FLB_IN(self, value=None): return
    def LFC_T_GLY_FLB_OUT(self, value=None): return
    def LFC_T_GLY_RFAMP1_IN(self, value=None): return
    def LFC_T_GLY_RFAMP1_OUT(self, value=None): return    
    def LFC_T_GLY_RFAMP2_IN(self, value=None): return
    def LFC_T_GLY_RFAMP2_OUT(self, value=None): return
    def LFC_YJ_OR_HK(self, value=None): return
    def LFC_YJ_SHUTTER(self, value=None): return
    def LFC_PMP_ATT(self, value=None): return



    def LFC_RIO_T(self, value=None):
        from Hardware.ORIONLaser import ORIONLaser
        rio = ORIONLaser(addr=f'ASRL{14}::INSTR')
        rio.connect()

        if value == None:
            
            ii=rio.readTECsetpoint()
            print(f'RIO_T: {ii} C')
            rio.disconnect()
            return ii
            #rio.printStatus()
        else:
            return 0 # not testing MODIFY for now
            rio.writeTECsetpoint(value)
            # need set default
            ii=rio.readTECsetpoint()
            return ii
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
        from Hardware.ORIONLaser import ORIONLaser
        rio = ORIONLaser(addr=f'ASRL{14}::INSTR')
        rio.connect()

        if value == None:
            
            ii=rio.readLaserdiodeCur_mA()
            print(f'RIO_I: {ii}mA')
            rio.disconnect()
            return ii
            #rio.printStatus()
        else:
            return 0 # not testing MODIFY for now
            rio.writeLaserdiodeCur_mA(value)
            # need set default
            ii=rio.readLaserdiodeCur_mA()
            return ii

    def LFC_EDFA27_P(self, value=None):
        return
        from Hardware.AmonicsEDFA import AmonicsEDFA
        amonic27 = AmonicsEDFA(addr=f'ASRL{6}::INSTR', name='Amonics EDFA 27 dBm')
        amonic27.connect()
        if value == None:
            
            edfa27p=amonic27.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic27.disconnect()
            return edfa27p
            #rio.printStatus()
        else:
            return 0 # not testing MODIFY for now
            amonic27._setChMode('acc')
            amonic27.accCh1Cur=value

            edfa27p=amonic27.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic27.disconnect()
            return edfa27p


    def LFC_EDFA27_ONOFF(self, value=None):
        return
        from Hardware.AmonicsEDFA import AmonicsEDFA
        amonic27 = AmonicsEDFA(addr=f'ASRL{6}::INSTR', name='Amonics EDFA 27 dBm')
        amonic27.connect()
        if value == None:
            
            edfa27onoff=amonic27.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic27.disconnect()
            return edfa27onoff
            #rio.printStatus()
        else:
            return 0 # not testing MODIFY for now
            amonic27.accCh1Status=value
            edfa27onoff=amonic27.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic27.disconnect()
            return edfa27onoff

    def LFC_EDFA13_P(self, value=None):
        return
        from Hardware.AmonicsEDFA import AmonicsEDFA
        amonic13 = AmonicsEDFA(addr=f'ASRL{9}::INSTR', name='Amonics EDFA 13 dBm')
        amonic13.connect()

        if value == None:
            
            edfa27p=amonic13.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic13.disconnect()
            return edfa27p
            #rio.printStatus()
        else:
            return 0 # not testing MODIFY for now
            amonic13._setChMode('acc')
            amonic13.accCh1Cur=value

            edfa27p=amonic13.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic13.disconnect()
            return edfa27p

    def LFC_EDFA13_ONOFF(self, value=None):
        return
        from Hardware.AmonicsEDFA import AmonicsEDFA
        amonic13 = AmonicsEDFA(addr=f'ASRL{9}::INSTR', name='Amonics EDFA 13 dBm')
        amonic13.connect()

        if value == None:
            
            edfa27onoff=amonic13.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic13.disconnect()
            return edfa27onoff
            #rio.printStatus()
        else:
            return 0 # not testing MODIFY for now
            amonic13.accCh1Status=value
            edfa27onoff=amonic13.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic13.disconnect()
            return edfa27onoff

    def LFC_EDFA23_P(self, value=None):
        return
        from Hardware.AmonicsEDFA import AmonicsEDFA
        amonic23 = AmonicsEDFA(addr=f'ASRL{12}::INSTR', name='Amonics EDFA 23 dBm')
        amonic23.connect()

        if value == None:
            
            edfa27p=amonic23.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic23.disconnect()
            return edfa27p
            #rio.printStatus()
        else:
            return 0 # not testing MODIFY for now
            amonic23._setChMode('acc')
            amonic23.accCh1Cur=value

            edfa27p=amonic23.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic23.disconnect()
            return edfa27p

    def LFC_EDFA23_ONOFF(self, value=None):
        return
        from Hardware.AmonicsEDFA import AmonicsEDFA
        amonic23 = AmonicsEDFA(addr=f'ASRL{12}::INSTR', name='Amonics EDFA 23 dBm')
        amonic23.connect()

        if value == None:
            
            edfa27onoff=amonic23.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic23.disconnect()
            return edfa27onoff
            #rio.printStatus()
        else:
            return 0 # not testing MODIFY for now
            amonic23.accCh1Status=value
            edfa27onoff=amonic23.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic23.disconnect()
            return edfa27onoff

    def LFC_RFAMP_I(self, value=None):
        return
        from Hardware.InstekGppDCSupply import InstekGppDCSupply
        rfampPS = InstekGppDCSupply(addr=f'ASRL{4}::INSTR', name='RF amplifier PS 30V 4A')
        rfampPS.connect()

        if value == None:
            
            rfampPS_i=rfampPS.Iout1
            print(f'LFC_RFAMP_I : +{rfampPS_i}A')
            rfampPS.disconnect()
            return rfampPS_i
            #rio.printStatus()
        else:
            return 0 # not testing MODIFY for now
            rfampPS.Iout1=value
            rfampPS_i=rfampPS.Iout1
            print(f'LFC_RFAMP_I : +{rfampPS_i}A')
            rfampPS.disconnect()
            return rfampPS_i
            

    def LFC_RFAMP_V(self, value=None):
        return
        from Hardware.InstekGppDCSupply import InstekGppDCSupply
        rfampPS = InstekGppDCSupply(addr=f'ASRL{4}::INSTR', name='RF amplifier PS 30V 4A')
        rfampPS.connect()

        if value == None:
            
            rfampPS_i=rfampPS.Vout1
            print(f'LFC_RFAMP_V : +{rfampPS_i}V')
            rfampPS.disconnect()
            return rfampPS_i
            #rio.printStatus()
        else:
            return 0 # not testing MODIFY for now
            rfampPS.Vout1=value
            rfampPS_i=rfampPS.Vout1
            print(f'LFC_RFAMP_V : +{rfampPS_i}V')
            rfampPS.disconnect()
            return rfampPS_i

    def LFC_RFOSCI_I(self, value=None):
        return
        from Hardware.InstekGPD_4303S import InstekGPD_4303S
        rfoscPS = InstekGPD_4303S(addr='ASRL13::INSTR', name='RF oscilator PS, CH2 15V, CH3 1V')
        rfoscPS.connect()
        if value == None:
            
            rfoscPS_i=rfoscPS.Iout2
            rfoscPS.disconnect()
            return rfoscPS_i
            
        else:
            return 0 # not testing MODIFY for now
            rfoscPS.Iset2=value
            rfoscPS_i=rfoscPS.Iout2
            rfoscPS.disconnect()
            return rfoscPS_i

    def LFC_RFOSCI_V(self, value=None):
        return
        from Hardware.InstekGPD_4303S import InstekGPD_4303S
        rfoscPS = InstekGPD_4303S(addr='ASRL13::INSTR', name='RF oscilator PS, CH2 15V, CH3 1V')
        rfoscPS.connect()
        if value == None:
            
            rfoscPS_i=rfoscPS.Vout2
            rfoscPS.disconnect()
            return rfoscPS_i
            
        else:
            return 0 # not testing MODIFY for now
            rfoscPS.Vset2=value
            rfoscPS_i=rfoscPS.Vout2
            rfoscPS.disconnect()
            return rfoscPS_i

    def LFC_IM_BIAS(self, value=None):
        return
        from Hardware.SRS_SIM900 import SRS_SIM900, SRS_PIDcontrol_SIM960
        srs = SRS_SIM900(addr='GPIB0::2::INSTR')
        srs.connect()
        servo_IM = SRS_PIDcontrol_SIM960(srs, 3, name='Minicomb Intensity Lock Servo')
        if value == None:
            
            
            IM_bias=servo_IM.get_output_voltage()

            srs.disconnect()
            return IM_bias

        else:
            return 0 # not testing MODIFY for now
            servo_IM.manual_output=value

            IM_bias=servo_IM.get_output_voltage()

            srs.disconnect()
            return IM_bias

    def LFC_IM_RF_ATT(self, value=None):
        return
        from Hardware.InstekGPD_4303S import InstekGPD_4303S
        rfoscPS = InstekGPD_4303S(addr='ASRL13::INSTR', name='RF oscilator PS, CH2 15V, CH3 1V')
        rfoscPS.connect()
        if value == None:
            
            rfoscPS_i=rfoscPS.Vout3
            rfoscPS.disconnect()
            return rfoscPS_i
            
        else:
            return 0 # not testing MODIFY for now
            rfoscPS.Vset2=value
            rfoscPS_i=rfoscPS.Vout3
            rfoscPS.disconnect()
            return rfoscPS_i

    def LFC_WSP_PHASE(self, value=None):
        return
        if value != None:
            from Hardware.Waveshaper import Waveshaper
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
        return
        from Hardware.PritelAmp import PritelAmp
        ptamp = PritelAmp(addr=f'ASRL{7}::INSTR', name='Pritel Amp')
        ptamp.connect()
        if value != None:

            ptamp.preAmp = f'{value}'+'mA'
            pre_p=ptamp.preAmp
            ptamp.disconnect()
            return pre_p
        else:
            return 0 # not testing MODIFY for now
            pre_p=ptamp.preAmp
            ptamp.disconnect()
            return pre_p
    
    def LFC_PTAMP_PRE_I(self, value=None):
        return
    

    def LFC_PTAMP_OUT(self, value=None):
        return
        if value != None:

            from Hardware.PritelAmp import PritelAmp
            ptamp = PritelAmp(addr=f'ASRL{7}::INSTR', name='Pritel Amp')
            ptamp.connect()

            pre_out=ptamp.outputPwr_mW
            ptamp.disconnect()
            return pre_out
        else:
            return 0 # not testing MODIFY for now
            raise ValueError("LFC_PTAMP_OUT is read only")
            return

    def LFC_PTAMP_I(self, value=None):
        return

        from Hardware.PritelAmp import PritelAmp
        ptamp = PritelAmp(addr=f'ASRL{7}::INSTR', name='Pritel Amp')
        ptamp.connect()

        if value != None:

            ptamp.pwrAmp = f'{value}'+'A'
            ptamp.disconnect()
            return 1

        else:
            return 0 # not testing MODIFY for now
            ptamp=ptamp.pwrAmp
            ptamp.disconnect()
            return ptamp  # return

    def LFC_PTAMP_ONOFF(self, value=None):
        return

        from Hardware.PritelAmp import PritelAmp
        ptamp = PritelAmp(addr=f'ASRL{7}::INSTR', name='Pritel Amp')
        ptamp.connect()

        if value != None:

            ptamp.activation = value
            ptact = ptamp.activation
            ptamp.disconnect()
            return ptact

        else:
            return 0 # not testing MODIFY for now
            ptact=ptamp.activation
            ptamp.disconnect()
            return ptact  # return

    def LFC_PTAMP_LATCH(self, value=None):
        return
        if value == None:
            from Hardware.Arduino_relay import Arduino_relay
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
        return
        from Hardware.TEC_TC720 import TEC_TC720

        tec_ppln = TEC_TC720(addr=f'COM{22}', name='PPLN Doubler TEC (TC720)')
        tec_ppln.connect()

        if value == None:
            tppln=tec_ppln.get_temp()
            tec_ppln.disconnect()
            return tppln

        else:
            return 0 # not testing MODIFY for now
            tec_ppln.set_temp(value)
            tppln=tec_ppln.get_temp()
            tec_ppln.disconnect()
            return tppln

    def LFC_PPLN_T(self, value=None):
        return
        from Hardware.TEC_TC720 import TEC_TC720
        # tec_PPLN = TEC_TC720(addr='ASRL46::INSTR')
        tec_wg = TEC_TC720(addr='COM16', name='Octave Waveguide TEC (TC720)')
        tec_wg.connect()

        if value == None:
            twg=tec_wg.get_temp()
            tec_wg.disconnect()
            return twg

        else:
            return 0 # not testing MODIFY for now
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
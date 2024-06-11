from Hardware import *
import numpy as np
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sys
import os
icetest_mode = False
test_mode = True


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
    # currently, error occurs when "writing" values to array
    # but would ever array keyword used for "write"?
    # works fine with read-only

    # print(values,"entered to KTLarray")
    # print(type(values))
    if values == None:
        return ""
    else:
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
        # print('__getitem__ called for', key)

        val = self.funcs[key](value=None)

        if val != None: 
            # Store the keyword value in keywords dictionary
            self.keywords[key] = val
        
            return val
    
    def __setitem__(self, key, val):
        '''Write keywords.
        When keyword values are changed by KTL user, stores the value.'''
        # print('__setitem__ called for', key, val)
        if val != None: val = self.convert_type(self.types[key], val)
        
        try:
            status = self.funcs[key](value = val)
            if status == 0: 
                # device_value = self.funcs[key](value=None)
                # print('Device value for',key,device_value)
                # self.keywords[key] = device_value
                self.keywords[key] = val


            # if successful, store the keyword value
            # if status == 0: self.keywords[key] = val
            # elif status == -1: 
            #     # actually this is never called because writing a keyword value 
            #     # to a non-writable keyword is already blocked by KTL
            #     print('This is non-writable keyword')

            elif status == None:
                print('None returned for keyword ', key)
            # else: 
            #     print('Error detected in writing ', val, 'to ', key)
            #     print('status:', status, type(status))
        except Exception as e:
            print("Error in writing ", val, " to ", key)
            print(e)
    
    @staticmethod
    def convert_type(typ, val):
        '''
        Converts type of KTL keyword (string) to desired types.
        '''
        
        if typ == 'integer': return int(val)
        elif typ == 'double': return float(val)
        elif typ == 'enumerated': return int(val)
        elif typ == 'string': return str(val)
        elif typ == 'boolean': 
            if val in ['True', '1', 1, True] : return True
            else: return False
        elif typ =='double array': 
            values = val.split(" ")
            return [float(value) for value in values]
        else:
            print('Unrecognized type')
            raise Exception
        
    # KTL keywords Implementation

    ########## KTL Keywords Implementation ############
    ########## Below are the connection functions for device, interal use only. ##########

    def __LFC_RIO_connect(self, value=None):
        '''Connect to RIO laser'''
        from Hardware.ORIONLaser import ORIONLaser
        return ORIONLaser(addr=f'ASRL{14}::INSTR')
        
    def __LFC_EDFA27_connect(self, value=None):
        '''Connect to Amonics EDFA 27 dBm'''
        from Hardware.AmonicsEDFA import AmonicsEDFA
        return AmonicsEDFA(addr=f'ASRL{6}::INSTR', name='Amonics EDFA 27 dBm')
    
    def __LFC_EDFA13_connect(self, value=None):
        '''Connect to Amonics EDFA 13 dBm'''
        from Hardware.AmonicsEDFA import AmonicsEDFA
        return AmonicsEDFA(addr=f'ASRL{9}::INSTR', name='Amonics EDFA 13 dBm')
    
    def __LFC_EDFA23_connect(self, value=None):
        '''Connect to Amonics EDFA 23 dBm'''
        from Hardware.AmonicsEDFA import AmonicsEDFA
        return AmonicsEDFA(addr=f'ASRL{12}::INSTR', name='Amonics EDFA 23 dBm')
    
    def __LFC_RFAMP_connect(self, value=None):
        '''Connect to RF amplifier PS 30V 4A'''
        from Hardware.InstekGppDCSupply import InstekGppDCSupply
        return InstekGppDCSupply(addr=f'ASRL{4}::INSTR', name='RF amplifier PS 30V 4A')
    
    def __LFC_RFOSCI_connect(self, value=None):
        '''Connect to RF oscillator PS, CH2 15V, CH3 1V'''
        from Hardware.InstekGPD_4303S import InstekGPD_4303S
        return InstekGPD_4303S(addr='ASRL13::INSTR', name='RF oscilator PS, CH2 15V, CH3 1V')
    
    def __LFC_servo_connect(self, value=None):
        from Hardware.SRS_SIM900 import SRS_SIM900, SRS_PIDcontrol_SIM960
        return SRS_SIM900(addr='GPIB0::2::INSTR')
    
    def __LFC_IM_LOCK_connect(self, srs):
        '''Connect to Minicomb Intensity Lock Servo'''
        from Hardware.SRS_SIM900 import SRS_SIM900, SRS_PIDcontrol_SIM960
        srs.connect()
        return SRS_PIDcontrol_SIM960(srs, 3, name='Minicomb Intensity Lock Servo')
    
    def __LFC_WSP_connect(self, value=None):
        '''Connect to Waveshaper'''
        from Hardware.Waveshaper import Waveshaper
        return Waveshaper()
    
    def __LFC_PTAMP_connect(self, value=None):
        '''Connect to Pritel Amp'''
        from Hardware.PritelAmp import PritelAmp
        return PritelAmp(addr=f'ASRL{7}::INSTR', name='Pritel Amp')
    
    # def __LFC_TEC_PPLN_connect(self, value=None):
    #     '''Connect to PPLN Doubler TEC (TC720)'''
    #     from Hardware.TEC_TC720 import TEC_TC720
    #     return TEC_TC720(addr=f'COM{22}', name='PPLN Doubler TEC (TC720)')
    
    # def __LFC_TEC_WG_connect(self, value=None):
    #     '''Connect to Octave Waveguide TEC (TC720)'''
    #     from Hardware.TEC_TC720 import TEC_TC720
    #     return TEC_TC720(addr='COM16', name='Octave Waveguide TEC (TC720)')
    
    def __LFC_USB2408_0_connect(self, value=None):
        '''Connect to USB2408'''
        from Hardware.USB2408 import USB2408
        return USB2408(addr=0)
    
    def __LFC_USB2408_1_connect(self, value=None):
        '''Connect to USB2408'''
        from Hardware.USB2408 import USB2408
        return USB2408(addr=1)
    
    def __LFC_OSA_connect(self, value=None):
        '''Connect to OSA'''
        from Hardware.Agilent_86142B import Agilent_86142B
        return Agilent_86142B()
    
    def __LFC_ARDUINO_connect(self, value=None):
        '''Connect to Arduino relay'''
        from Hardware.Arduino_relay import Arduino_relay
        return Arduino_relay(addr=f"COM3")
    
    def __LFC_RB_LOCK_connect(self, srs):
        from Hardware.SRS_SIM900 import SRS_SIM900, SRS_PIDcontrol_SIM960
        srs.connect()
        return SRS_PIDcontrol_SIM960(srs, 5, name='Rio Laser Fceo Rb spectroscopy Lock Servo')
        
    def __LFC_2BY2_SWITCH_connect(self, value=None):
        from Hardware.Agiltron_2by2_switch import AgiltronSelfAlign22
        return AgiltronSelfAlign22(addr=f'COM{20}')

    def __LFC_OSC_connect(self, value=None):
        from Hardware.TDS2024C import TDS2024C
        return TDS2024C()
    
    def __LFC_KEYSIGHT_FG_connect(self, value=None):
        from Hardware.KeysightFG_33500 import KeysightFG_33500
        return KeysightFG_33500(addr='USB0::0x0957::0x2807::MY59003824::INSTR', name='Keysight FG 33500')
  
    def __LFC_HK_SHUTTER_connect(self, value=None):
        from Hardware.hk_shutter import hk_shutter
        return hk_shutter(addr='COM17')   #5,8,11,14,17

    def __LFC_VOA1550_connect(self, value=None):
        from Hardware.OZopticsVOA import OZopticsVOA
        return OZopticsVOA(addr=f'ASRL{15}::INSTR', name='1.55um VOA')

    def __VOA1310_connect(self, value=None):
        from Hardware.OZopticsVOA import OZopticsVOA
        return OZopticsVOA(addr=f'ASRL{19}::INSTR', name='1.31um VOA')
    
    def __VOA2000_connect(self, value=None):
        from Hardware.OZopticsVOA import OZopticsVOA
        return OZopticsVOA(addr=f'ASRL{18}::INSTR', name='2um VOA')
    
    def __LFC_CLARITY_connect(self, value=None):
        from Hardware.Clarity import Clarity
        return Clarity(addr=f'ASRL{23}::INSTR')
    
    def __LFC_PENDULEM_connect(self, value=None):
        from Hardware.PendulumCNT90 import PendulumCNT90
        return PendulumCNT90()
    
    def __LFC_TEC_PPLN_connect(self, value=None):
        from Hardware.TEC_TC720 import TEC_TC720
        return TEC_TC720(addr=f'COM{16}', name='PPLN Doubler TEC (TC720)')
        
    def __LFC_TEC_WVG_connect(self, value=None):
        from Hardware.TEC_TC720 import TEC_TC720
        return TEC_TC720(addr=f'COM{22}', name='WVG Doubler TEC (TC720)')

    
    def __sleep(self, value=0.5):
        import time
        time.sleep(value)
        return value
    
    def __sendemail(self,
                    mail_content,
                    subject='KECKLFC WARNING MESSAGE',
                    recv_address=['mgao@caltech.edu','jge2@caltech.edu','stephanie.leifer@aero.org', 'yjkim@astro.ucla.edu'],
                    files=['test.log',],
                    path=r'C:\Users\KeckLFC\Desktop\Keck\Logs'):


        # email_content = f'auto email test, message:{i}'
        # email_subject = 'KECKLFC WARNING MESSAGE'
        # email_list=['mgao@caltech.edu','jge2@caltech.edu']
        # path=r'C:\Users\KeckLFC\Desktop\Keck\Logs'
        # files=['test.log',]

        # param mail_content emial content
        # param recv_address receiver email address

        
        sender_address = 'kecklfc@gmail.com'
        sender_pass = 'onnp dhxb fhaz bmmm'

        toaddrs  = recv_address

        to_string =''
        for item in toaddrs:
            to_string += item +','
        # 
        message = MIMEMultipart() #message structure initialization
        message['From'] = sender_address #your email
        message['To'] = to_string #receiver email
        message['Subject'] = subject

        for file in files:
            if os.path.isfile(path + '/' + file):
                # create attachment
                att = MIMEText(open(path + '/' + file, 'rb').read(), 'base64', 'utf-8')
                att["Content-Type"] = 'application/octet-stream'
                att.add_header("Content-Disposition", "attachment", filename=("gbk", "", file))
                message.attach(att)
            # mail_content, can be self define,'plain' is the type of content
        message.attach(MIMEText(mail_content,'plain'))
        # smtp server, cen be seen in the gmail email setting
        session = smtplib.SMTP('smtp.gmail.com',587)
        # connect to tls
        session.starttls()
        # login email
        session.login(sender_address,sender_pass)
        # message text convey to structure
        text = message.as_string()
        # main function to send email
        session.sendmail(sender_address,recv_address,text)
        # print
        print("send {} successfully".format(recv_address))
        # close session
        session.quit()


#--------------------------connection above----------------------------------------------
#--------------------------functions below----------------------------------------------



    def LFC_TEMP_TEST1(self, value=None):
        if test_mode: return
        if value == None:
            daq1 = self.__LFC_USB2408_0_connect()
            daq1.connect()    
            temp1 = daq1.get_temp_all()
            daq0_list=["Rack side buffle (middle side rack)", "Waveshaper (upper rack)",
                                           "Rb clock (middle rack)", "Pritel (middle upper rack)",
                                           "Rack Glycol out", "Rack Glycol in",
                                           "Power Supply Shelf (bottom rack)", "Unconnected"]
    
            # print(temp1)
            daq1.disconnect()
            print(self.keywords['LFC_TEMP_TEST1'], type(self.keywords['LFC_TEMP_TEST1']))
            return KTLarray(temp1)
        else:
            return 0

    def LFC_TEMP_TEST2(self, value=None):
        if test_mode: return

        if value == None:
            daq1 = self.__LFC_USB2408_1_connect()
            daq1.connect()
            daq1_list=["RF Oscillator", "RF amplifier", 
                "Main Phase Modulators", "Filter Cavity",
                 "Board Glycol out", "Board Glycol in",
                "Compression Stage","Rubidium (Rb) Cell D2-210"]
            temp1 = daq1.get_temp_all()
            # print(temp1)
            daq1.disconnect()
            return KTLarray(temp1)
        else:
            return 0

    def LFC_T_GLY_RACK_IN(self, value=None):
        if test_mode: return

        if value == None:
            # print(self.keywords['LFC_TEMP_TEST1'])
            # return self.keywords['LFC_TEMP_TEST1'].split(" ")[5]

            all_temperatures = self.convert_type('double array', self.keywords['LFC_TEMP_TEST1'])#.split(' ')
            return all_temperatures[5]

            # addr = 0
            # chan = 5
            # daq = self.__LFC_USB2408_0_connect()
            # daq.connect()
            # temp = daq.get_temp(chan)
            # daq.disconnect()
            return 0 #temp
        else:
            return 0
        
    def LFC_T_GLY_RACK_OUT(self, value=None):
        if test_mode: return

        if value == None:
            all_temperatures = self.convert_type('double array', self.keywords['LFC_TEMP_TEST1'])#.split(' ')
            print(all_temperatures)
            return all_temperatures[4]
            addr = 0
            chan = 4
            daq = self.__LFC_USB2408_0_connect()
            daq.connect()
            temp = daq.get_temp(chan)
            daq.disconnect()
            return temp
        else:
            return 0
            # raise ValueError("LFC_T_GLY_RACK_OUT is read-only")
            # return
        
    def LFC_T_EOCB_IN(self, value=None):
        if test_mode: return

        if value == None:
            all_temperatures = self.convert_type('double array', self.keywords['LFC_TEMP_TEST2'])#.split(' ')
            return all_temperatures[5]
            addr = 1
            chan = 5
            daq = self.__LFC_USB2408_1_connect()
            daq.connect()
            temp = daq.get_temp(chan)
            daq.disconnect()
            return temp
        else:
            return 0
            # raise ValueError("LFC_T_EOCB_IN is read-only")
            # return

    def LFC_T_EOCB_OUT(self, value=None):
        if test_mode: return

        if value == None:
            all_temperatures = self.convert_type('double array', self.keywords['LFC_TEMP_TEST2'])#.split(' ')
            return all_temperatures[4]
            addr = 1
            chan = 4
            daq = self.__LFC_USB2408_1_connect()
            daq.connect()
            temp = daq.get_temp(chan)
            daq.disconnect()
            return temp
        else:
            return 0
            # raise ValueError("LFC_T_EOCB_OUT is read-only")
            # return
        
    def LFC_T_RACK_TOP(self, value=None):
        if test_mode: return

        if value == None:
            all_temperatures = self.convert_type('double array', self.keywords['LFC_TEMP_TEST1'])#.split(' ')
            return all_temperatures[3]
            addr = 0
            chan = 3 # Use Pritel Amplifier TEC as the rack top temperature
            daq = self.__LFC_USB2408_0_connect()
            daq.connect()
            temp = daq.get_temp(chan)
            daq.disconnect()
            return temp
        else:
            return 0
            # raise ValueError("LFC_T_RACK_TOP is read-only")
            # return
        
    def LFC_T_RACK_MID(self, value=None):
        if test_mode: return

        if value == None:
            all_temperatures = self.convert_type('double array', self.keywords['LFC_TEMP_TEST1'])#.split(' ')
            return all_temperatures[0]
            addr = 0
            chan = 0 # Use Side buffle as the rack mid temperature
            daq = self.__LFC_USB2408_0_connect()
            daq.connect()
            temp = daq.get_temp(chan)
            daq.disconnect()
            return temp
        else:
            return 0
            # raise ValueError("LFC_T_RACK_MID is read-only")
            # return
    
    def LFC_T_RACK_BOT(self, value=None):
        if test_mode: return

        if value == None:
            all_temperatures = self.convert_type('double array', self.keywords['LFC_TEMP_TEST1'])#.split(' ')
            return all_temperatures[6]
            addr = 0
            chan = 6 # Bottom rack temperature
            daq = self.__LFC_USB2408_0_connect()
            daq.connect()
            temp = daq.get_temp(chan)
            daq.disconnect()
            return temp
        else:
            return 0
            # raise ValueError("LFC_T_RACK_BOT is read-only")
            # return
        
    def LFC_TEMP_MONITOR(self,value=None):#TBD
        if test_mode: return 
        # return
        if value == None:
            temp_1= self.convert_type('double array', self.keywords['LFC_TEMP_TEST1'])#.split(' ')
            #temp_2=self.keywords['LFC_TEMP_TEST2']
        

            threshold=0
            if (temp_1[1])>threshold:
                #self.LFC_CLOSE_ALL(1)
                self.__sendemail('Temperature is too high, all devices are closed,test only')
                return 0
            else:
                return 1
            # if temp_2[1]>threshold:
            #     self.LFC_CLOSE_ALL(1)
            #     self.__sendemail('Temperature is too high, all devices are closed')

    
    
    def LFC_RFOSCI_MONITOR(self,value=None): #TBD
        if test_mode: return
        # return
        rfosci_threshold_v=15
        rfosci_threshold_i=0.4
        if value == None:
            if self.keywords['LFC_RFOSCI_ONOFF'] == 1:
                voltage=self.LFC_RFOSCI_V()
                current=self.LFC_RFOSCI_I()
                if np.abs(voltage-rfosci_threshold_v)>1 or np.abs(current-rfosci_threshold_i)>0.1:
                    self.LFC_CLOSE_ALL(1)
                    self.__sendemail('RF oscillator is off due to over voltage or over current')
                    return 1

        else:
            return 0
        
    def LFC_RFAMP_MONITOR(self,value=None): #TBD
        if test_mode: return
        # return
        rfamp_threshold_v=30
        rfamp_threshold_i=4.5
        if value == None:
            if self.keywords['LFC_RFAMP_ONOFF'] == 1:
                voltage=self.LFC_RFAMP_V()
                current=self.LFC_RFAMP_I()
                if np.abs(voltage-rfamp_threshold_v)>1 or np.abs(current-rfamp_threshold_i)>0.1:
                    self.LFC_CLOSE_ALL(1)
                    self.__sendemail('RF amplifier is off due to over voltage or over current')
                    return 1
                
        else:
            return 0
        
    def LFC_RF_FREQ_MONITOR(self,value=None): #TBD
        if test_mode: return
        # return
        rf_freq_threshold=16e9
        if value == None:
            if (self.keywords['LFC_RFAMP_ONOFF'] == 1) and (self.keywords['LFC_RFOSCI_ONOFF'] == 1):

                freq=self.LFC_PENDULEM_FREQ()
                if np.abs(freq-rf_freq_threshold)>10:
                    self.LFC_CLOSE_ALL(1)
                    self.__sendemail('RF frequency is not 16 GHz, all devices are closed')
                    return 1
        else:
            return 0

    def LFC_CLOSE_ALL(self, value=None):
        return
        if value==1:
            self.LFC_PTAMP_ONOFF(0)
            self.LFC_EDFA23_ONOFF(0)
            self.LFC_EDFA27_ONOFF(0)
            self.LFC_RFAMP_ONOFF(0)
            self.LFC_RFOSCI_ONOFF(0)
            self.LFC_CLARITY_ONOFF(0)
            self.__sendemail('All devices are closed')

        


    def LFC_CLARITY_ONOFF(self, value=None):#test read
        # boolean to enumerated
        if test_mode: return

        if value == None:
            clarity = self.__LFC_CLARITY_connect()
            status = clarity.get_status()
            return status
        else:
            clarity = self.__LFC_CLARITY_connect()
            status=clarity.set_onoff(value)
            return 0 #status



    def LFC_T_GLY_EOCB_IN(self, value=None): return
    def LFC_T_GLY_EOCB_OUT(self, value=None): return
    def LFC_T_GLY_FLB_IN(self, value=None): return
    def LFC_T_GLY_FLB_OUT(self, value=None): return
    def LFC_T_GLY_RFAMP1_IN(self, value=None): return
    def LFC_T_GLY_RFAMP1_OUT(self, value=None): return    
    def LFC_T_GLY_RFAMP2_IN(self, value=None): return
    def LFC_T_GLY_RFAMP2_OUT(self, value=None): return
    def LFC_YJ_OR_HK(self, value=None): return
    # def LFC_YJ_SHUTTER(self, value=None): return
    def LFC_PMP_ATT(self, value=None): return



    def LFC_RIO_T(self, value=None):
        # KEYWORD READ tested
        if test_mode: return
        rio = self.__LFC_RIO_connect()
        

        if value == None:
            rio.connect()
            ii=rio.readTECsetpoint()
            print(f'RIO_T: {ii} C')
            rio.disconnect()
            return ii
            #rio.printStatus()
        else:
            # if test_mode: return
            #return 0 # not testing MODIFY for now
            rio.connect()
            rio.writeTECsetpoint(value)
            return 0
            # self.__sleep(0.5)
            # # need set default
            # ii=rio.readTECsetpoint()
            # return ii

    def LFC_RIO_I(self, value=None):
        if test_mode: return
        rio = self.__LFC_RIO_connect()
        

        if value == None:
            rio.connect()
            ii=rio.readLaserdiodeCur_mA()
            print(f'RIO_I: {ii}mA')
            rio.disconnect()
            return ii
            #rio.printStatus()
        else:

            #return 0 # not testing MODIFY for now
            rio.connect()
            rio.writeLaserdiodeCur_mA(value)
            # need set default
            self.__sleep(0.5)
            ii=rio.readLaserdiodeCur_mA()
            return ii

    def LFC_EDFA27_P(self, value=None): #test read- complete
        if test_mode: return

        amonic27 = self.__LFC_EDFA27_connect()
        
        
        if value == None:
            amonic27.connect()
            edfa27p=amonic27.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic27.disconnect()
            return edfa27p
            #rio.printStatus()

        elif value == 'default':
            amonic27.connect()
            amonic27._setChMode('apc')
            self.__sleep(0.5)
            amonic27.accCh1Cur='450mw'
            self.__sleep(0.5)

            edfa27autoset=amonic27.accCh1Cur
            
            amonic27.disconnect()
            return edfa27autoset
        else:
            if test_mode: return
            #return 0 # not testing MODIFY for now
            amonic27.connect()
            amonic27._setChMode('apc')
            amonic27.accCh1Cur=f'{value}mw'

            self.__sleep(0.5)
            edfa27p=amonic27.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic27.disconnect()
            return edfa27p
        
    def LFC_EDFA27_P_DEFAULT(self, value=None): #test r w # not implemented
        if test_mode: return
        amonic27 = self.__LFC_EDFA27_connect()
        
        if value == None:
            amonic27.connect()
            edfa27p=amonic27.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic27.disconnect()
            return edfa27p
        else:
            amonic27.connect()
            amonic27._setChMode('apc')
            self.__sleep(0.5)
            amonic27.accCh1Cur='450mw'
            self.__sleep(0.5)

            edfa27autoset=amonic27.accCh1Cur
            
            amonic27.disconnect()
            return 0 #edfa27autoset

            
        
    def LFC_EDFA27_AUTO_ON(self, value=None): #test r
        if test_mode: return
        amonic27 = self.__LFC_EDFA27_connect()
        

        if value==None:
            amonic27.connect()
            edfa27p=amonic27.outputPowerCh1
            #print(f'EDFA27 : {edfa27p}mw')
            amonic27.disconnect()
            return edfa27p
        elif value == 1:
            amonic27.connect()
            amonic27._setChMode('apc')
            self.__sleep(0.5)
            amonic27.accCh1Cur='450mw'
            self.__sleep(0.5)
            amonic27.accCh1Status=1
            amonic27.activation=1
            self.__sleep(0.5)
            edfa27autoset=amonic27.accCh1Cur
            
            amonic27.disconnect()
            return edfa27autoset
        else:
            return 

 


    def LFC_EDFA27_ONOFF(self, value=None):# test r
        if test_mode: return
        
        amonic27 = self.__LFC_EDFA27_connect()
        
        if value == None:
            amonic27.connect()
            edfa27onoff=amonic27.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic27.disconnect()
            return edfa27onoff
            #rio.printStatus()
        else:
            if test_mode: return
            amonic27.connect()
            #return 0 # not testing MODIFY for now
            amonic27.accCh1Status=value
            amonic27.activation=value
            self.__sleep(0.5)
            edfa27onoff=amonic27.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic27.disconnect()
            return edfa27onoff

    def LFC_EDFA13_P(self, value=None):
        if test_mode: return
        amonic13 = self.__LFC_EDFA13_connect()
        

        if value == None:
            amonic13.connect()
            edfa13p=amonic13.outputPowerCh1
            print(f'EDFA27 : {edfa13p}mw')
            amonic13.disconnect()
            return edfa13p
            #rio.printStatus()
        else:
            #return 0 # not testing MODIFY for now
            amonic13.connect()
            amonic13._setChMode('apc')
            amonic13.accCh1Cur=value
            self.__sleep(0.5)
            edfa13p=amonic13.outputPowerCh1
            print(f'EDFA27 : {edfa13p}mw')
            amonic13.disconnect()
            return edfa13p

    def LFC_EDFA13_ONOFF(self, value=None):
        if test_mode: return
        amonic13 = self.__LFC_EDFA13_connect()
        

        if value == None:
            amonic13.connect()
            edfa27onoff=amonic13.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic13.disconnect()
            return edfa27onoff
            #rio.printStatus()
        else:
            #return 0 # not testing MODIFY for now
            amonic13.connect()
            amonic13.accCh1Status=value
            self.__sleep(0.5)
            edfa27onoff=amonic13.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic13.disconnect()
            return edfa27onoff

    def LFC_EDFA23_P(self, value=None): # test r
        if test_mode: return
        amonic23 = self.__LFC_EDFA23_connect()
        

        if value == None:
            amonic23.connect()
            edfa27p=amonic23.outputPowerCh1
            print(f'EDFA23 : {edfa27p}mw')
            amonic23.disconnect()
            return edfa27p
            #rio.printStatus()

        elif value == 'default':
            amonic23.connect()
            amonic23._setChMode('acc')
            amonic23.accCh1Cur='80mA'
            self.__sleep(0.5)
            edfa27autoset=amonic23.accCh1Cur
            amonic23.disconnect()
            return edfa27autoset
        else:
            #return 0 # not testing MODIFY for now
            amonic23.connect()
            amonic23._setChMode('acc')
            amonic23.accCh1Cur=value
            self.__sleep(0.5)
            edfa27p=amonic23.outputPowerCh1
            print(f'EDFA27 : {edfa27p}mw')
            amonic23.disconnect()
            return edfa27p

    def LFC_EDFA23_ONOFF(self, value=None): #test r
        if test_mode: return
        amonic23 = self.__LFC_EDFA23_connect()
        

        if value == None:
            amonic23.connect()
            edfa27onoff=amonic23.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic23.disconnect()
            return edfa27onoff
            #rio.printStatus()
        else:
            #return 0 # not testing MODIFY for now
            amonic23.connect()
            amonic23.accCh1Status=value
            amonic23.activation=value
            self.__sleep(0.5)
            edfa27onoff=amonic23.accCh1Status
            print(f'EDFA27 : '+edfa27onoff)
            amonic23.disconnect()
            return edfa27onoff
        
    def LFC_EDFA23_P_DEFAULT(self, value=None): #test r w
        if test_mode: return
        amonic23 = self.__LFC_EDFA23_connect()
        

        if value == None:
            amonic23.connect()
            edfa27p=amonic23.outputPowerCh1
            #print(f'EDFA27 : {edfa27p}mw')
            amonic23.disconnect()
            return edfa27p
        else:
            amonic23.connect()
            amonic23._setChMode('acc')
            self.__sleep(0.5)
            amonic23.accCh1Cur='80mA'
            self.__sleep(0.5)
            edfa27autoset=amonic23.accCh1Cur
            
            amonic23.disconnect()
            return edfa27autoset
        
    def LFC_EDFA23_AUTO_ON(self, value=None): #test r
        if test_mode: return
        amonic23 = self.__LFC_EDFA23_connect()
        

        if value==None:
            amonic23.connect()
            edfa27p=amonic23.outputPowerCh1
            #print(f'EDFA27 : {edfa27p}mw')
            amonic23.disconnect()
            return edfa27p
        elif value == 1:
            amonic23.connect()
            amonic23._setChMode('acc')
            self.__sleep(0.5)
            amonic23.accCh1Cur='80mA'
            self.__sleep(0.5)
            amonic23.accCh1Status=1
            amonic23.activation=1
            self.__sleep(0.5)
            edfa27autoset=amonic23.accCh1Cur
            
            amonic23.disconnect()
            return edfa27autoset
        else:
            return


    def LFC_RFAMP_I(self, value=None): #test r
        if test_mode: return
        rfampPS = self.__LFC_RFAMP_connect()
        

        if value == None:
            rfampPS.connect()
            rfampPS_i=rfampPS.Iout1
            print(f'LFC_RFAMP_I : +{rfampPS_i}A')
            rfampPS.disconnect()
            return rfampPS_i
            #rio.printStatus()

        elif value == 'default':
            rfampPS.connect()
            rfampPS.Iout1=5
            self.__sleep(0.5)
            rfampPS_i=rfampPS.Iout1
            print(f'LFC_RFAMP_I : +{rfampPS_i}A')
            rfampPS.disconnect()
            return rfampPS_i
        else:
            #return 0 # not testing MODIFY for now
            rfampPS.connect()
            rfampPS.Iout1=value
            self.__sleep(0.5)
            rfampPS_i=rfampPS.Iout1
            print(f'LFC_RFAMP_I : +{rfampPS_i}A')
            rfampPS.disconnect()
            return rfampPS_i
            

    def LFC_RFAMP_V(self, value=None): #test r, don't test w
        if test_mode: return
        rfampPS = self.__LFC_RFAMP_connect()
        

        if value == None:
            rfampPS.connect()
            rfampPS_i=rfampPS.Vout1
            print(f'LFC_RFAMP_V : +{rfampPS_i}V')
            rfampPS.disconnect()
            return rfampPS_i
            #rio.printStatus()

        elif value == 'default':
            rfampPS.connect()
            rfampPS.Vout1=30
            self.__sleep(0.5)
            rfampPS_i=rfampPS.Vout1
            #print(f'LFC_RFAMP_V : +{rfampPS_i}V')
            rfampPS.disconnect()
            return rfampPS_i

        else:
            #return 0 # not testing MODIFY for now
            rfampPS.connect()
            rfampPS.Vout1=value
            self.__sleep(0.5)
            rfampPS_i=rfampPS.Vout1
            print(f'LFC_RFAMP_V : +{rfampPS_i}V')
            rfampPS.disconnect()
            return rfampPS_i
        
    def LFC_RFAMP_DEfAULT(self, value=None): #test r
        if test_mode: return
        rfampPS = self.__LFC_RFAMP_connect()
        

        if value == None:
            rfampPS.connect()
            rfampPS_v=rfampPS.Vout1
            print(f'LFC_RFAMP_V : +{rfampPS_i}V')
            self.__sleep(0.5)
            rfampPS_i=rfampPS.Iout1
            print(f'LFC_RFAMP_I : +{rfampPS_i}A')
            rfampPS.disconnect()
            return rfampPS_v, rfampPS_i
            #rio.printStatus(

        else:
            #return 0 # not testing MODIFY for now
            rfampPS.connect()
            rfampPS.Vout1=30
            self.__sleep(0.5)
            rfampPS.Iout1=5
            rfampPS_v=rfampPS.Vout1
            rfampPS_i=rfampPS.Iout1
            #print(f'LFC_RFAMP_V : +{rfampPS_i}V')
            rfampPS.disconnect()
            return rfampPS_v, rfampPS_i
        
    def LFC_RFAMP_ONOFF(self, value=None):# test r
        if test_mode: return
        rfampPS = self.__LFC_RFAMP_connect()
        
        if value == None:
            rfampPS.connect()
            rfampPS_i=rfampPS.activation1
            rfampPS.disconnect()
            return rfampPS_i
            #rio.printStatus()

        else:
            #return 0 # not testing MODIFY for now
            rfampPS.connect()
            rfampPS.activation1=value
            self.__sleep(0.5)
            rfampPS_i=rfampPS.activation1
            rfampPS.disconnect()
            return rfampPS_i

    def LFC_RFOSCI_I(self, value=None): #test r
        if test_mode: return
        rfoscPS = self.__LFC_RFOSCI_connect()
        
        if value == None:
            rfoscPS.connect()
            rfoscPS_i=rfoscPS.Iout2
            rfoscPS.disconnect()
            return rfoscPS_i
        
        elif value == 'default':
            rfoscPS.connect()
            rfoscPS.Iset2=3
            self.__sleep(0.5)
            rfoscPS_i=rfoscPS.Iout2
            rfoscPS.disconnect()
            return rfoscPS_i
        else:
            #return 0 # not testing MODIFY for now
            rfoscPS.connect()
            rfoscPS.Iset2=value
            self.__sleep(0.5)
            rfoscPS_i=rfoscPS.Iout2
            rfoscPS.disconnect()
            return rfoscPS_i

    def LFC_RFOSCI_V(self, value=None): #test r
        if test_mode: return
        rfoscPS = self.__LFC_RFOSCI_connect()
        
        if value == None:
            rfoscPS.connect()
            rfoscPS_i=rfoscPS.Vout2
            rfoscPS.disconnect()
            return rfoscPS_i
            
        elif value == 'default':
            rfoscPS.connect()
            rfoscPS.Vset2=15
            self.__sleep(0.5)
            rfoscPS_v=rfoscPS.Vout2
            rfoscPS.disconnect()
            return rfoscPS_v
        else:
            #return 0 # not testing MODIFY for now
            rfoscPS.connect()
            rfoscPS.Vset2=value
            self.__sleep(0.5)
            rfoscPS_i=rfoscPS.Vout2
            rfoscPS.disconnect()
            return rfoscPS_i
        
    def LFC_RFOSCI_DEFAULT(self, value=None): #test r
        if test_mode: return
        
        if value == None:
            rfoscPS = self.__LFC_RFOSCI_connect()
            rfoscPS.connect()
            rfoscPS_v=rfoscPS.Vout2
            rfoscPS_i=rfoscPS.Iout2
            rfoscPS.disconnect()
            return rfoscPS_v, rfoscPS_i
            
        else:
            rfoscPS = self.__LFC_RFOSCI_connect()
            rfoscPS.connect()
            rfoscPS.Vset2=15
            self.__sleep(0.5)
            rfoscPS.Iset2=3
            self.__sleep(0.5)
            rfoscPS_v=rfoscPS.Vout2
            rfoscPS_i=rfoscPS.Iout2
            rfoscPS.disconnect()
            return rfoscPS_v, rfoscPS_i
        
    def LFC_RFOSCI_ONOFF(self, value=None): #test r
        if test_mode: return
        rfoscPS = self.__LFC_RFOSCI_connect()
        
        if value == None:
            rfoscPS.connect()
            rfoscPS_i=rfoscPS.activation
            rfoscPS.disconnect()
            return rfoscPS_i
            
        else:
            #return 0 # not testing MODIFY for now
            rfoscPS.connect()
            rfoscPS.activation=value
            self.__sleep(0.5)
            rfoscPS_i=rfoscPS.activation
            rfoscPS.disconnect()
            return rfoscPS_i

    def LFC_IM_BIAS(self, value=None): #test r
        if test_mode: return
        
        if value == None:
            srs = self.__LFC_servo_connect()
            servo_IM = self.__LFC_IM_LOCK_connect(srs)
            servo_IM.connect()
            
            IM_bias=servo_IM.get_output_voltage()
            servo_IM.disconnect()
            srs.disconnect()
            return IM_bias

        else:
            #return 0 # not testing MODIFY for now
            srs = self.__LFC_servo_connect()
            servo_IM = self.__LFC_IM_LOCK_connect(srs)
            servo_IM.connect()
            servo_IM.manual_output=value
            self.__sleep(0.5)
            IM_bias=servo_IM.get_output_voltage()
            servo_IM.disconnect()
            srs.disconnect()
            return IM_bias

    def LFC_IM_RF_ATT(self, value=None): #test r
        if test_mode: return
        rfoscPS = self.__LFC_RFOSCI_connect()
        
        if value == None:
            rfoscPS.connect()
            rfoscPS_i=rfoscPS.Vout3
            rfoscPS.disconnect()
            return rfoscPS_i
            
        elif value == 'default':
            rfoscPS.connect()
            rfoscPS.Vset3=0.72
            self.__sleep(0.5)
            rfoscPS_i=rfoscPS.Vout3
            rfoscPS.disconnect()
            return rfoscPS_i
        else:
            #return 0 # not testing MODIFY for now
            rfoscPS.connect()
            rfoscPS.Vset3=value
            self.__sleep(0.5)
            rfoscPS_i=rfoscPS.Vout3
            rfoscPS.disconnect()
            return rfoscPS_i

    def LFC_WSP_PHASE(self, value=None):#TBD
        if test_mode: return
        #return
        
        if value != None:
            ws = self.__LFC_WSP_connect()
            ws.connect()

            d2 = value
            ws.set3rdDisper(d2,d3=0.)
            ws.disconnect()
            return 1

        else:
            # ws need recheck
            return 0

    def LFC_WSP_ATTEN(self, value=None): #TBD
        if test_mode: return
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

    def LFC_PTAMP_PRE_P(self, value=None): #test r
        if test_mode: return
        #return
        ptamp=self.__LFC_PTAMP_connect()
        
        if value != None:
            ptamp.connect()
            ptamp.preAmp = f'{value}'+'mA'
            self.__sleep(0.5)
            pre_p=ptamp.preAmp
            ptamp.disconnect()
            return pre_p
        elif value == 'default':
            ptamp.connect()
            ptamp.preAmp = '600mA'
            self.__sleep(0.5)
            pre_p=ptamp.preAmp
            ptamp.disconnect()
            return pre_p
        else:
            #return 0 # not testing MODIFY for now
            ptamp.connect()
            pre_p=ptamp.preAmp
            ptamp.disconnect()
            return pre_p
        
    def LFC_PTAMP_PRE_P_DEFAULT(self, value=None): #test r
        if test_mode: return
        ptamp=self.__LFC_PTAMP_connect()
        
        if value == None:
            ptamp.connect()
            pre_p=ptamp.preAmp
            ptamp.disconnect()
            return pre_p
        else:
            ptamp.connect()
            ptamp.preAmp = '600mA'
            self.__sleep(0.5)
            pre_p=ptamp.preAmp
            ptamp.disconnect()
            return pre_p
    
    def LFC_PTAMP_PRE_I(self, value=None):#no such function
        if test_mode: return
        return
    

    def LFC_PTAMP_OUT(self, value=None): #test r
        if test_mode: return
        #return
        ptamp=self.__LFC_PTAMP_connect()
        if value != None:

            ptamp.connect()

            pre_out=ptamp.outputPwr_mW
            ptamp.disconnect()
            return pre_out
        else:
            #return 0 # not testing MODIFY for now
            raise ValueError("LFC_PTAMP_OUT is read only")
            return

    def LFC_PTAMP_I(self, value=None): #test r
        if test_mode: return
        #return

        ptamp=self.__LFC_PTAMP_connect()
        

        if value != None:
            ptamp.connect()
            ptamp.pwrAmp = f'{value}'+'A'
            self.__sleep(0.5)
            ptamp1=ptamp.pwrAmp
            ptamp.disconnect()
            return ptamp1

        elif value == 'default':
            ptamp.connect()
            ptamp.pwrAmp = '3.8A'
            self.__sleep(0.5)
            ptamp1=ptamp.pwrAmp
            ptamp.disconnect()
            return ptamp1
        else:
            #return 0 # not testing MODIFY for now
            ptamp.connect()
            ptamp=ptamp.pwrAmp
            ptamp.disconnect()
            return ptamp  # return
        
    def LFC_PTAMP_I_DEFAULT(self, value=None): #test r
        if test_mode: return
        ptamp=self.__LFC_PTAMP_connect()
       
        if value == None: 
            ptamp.connect()
            ptamp1=ptamp.pwrAmp
            ptamp.disconnect()
            return ptamp1
        else:
            ptamp.connect()
            ptamp.pwrAmp = '4.1A'
            self.__sleep(0.5)
            ptamp1=ptamp.pwrAmp
            ptamp.disconnect()
            return ptamp1

    def LFC_PTAMP_ONOFF(self, value=None):# test r
        if test_mode: return
        ptamp=self.__LFC_PTAMP_connect()
        

        if value != None:
            ptamp.connect()
            ptamp.activation = value
            self.__sleep(0.5)
            ptact = ptamp.activation
            ptamp.disconnect()
            return ptact

        else:
            #return 0 # not testing MODIFY for now
            ptamp.connect()
            ptact=ptamp.activation
            ptamp.disconnect()
            return ptact  # return

    def LFC_PTAMP_LATCH(self, value=None):#test r 
        if test_mode: return
        #return
        arduino = self.__LFC_ARDUINO_connect()
        if value == None:
            arduino.connect()
            message=arduino.get_relay_status()
            self.__sleep(0.5)
            if message =="relay sending OK_to_Amplify signal to amplifier":
                message=1
            elif message =="relay is STOPPING amplifier, but will be OK_to_Amplify after reset_relay_latch.":
                message=0
            elif message =="relay is STOPPING amplifier, because input power is too low":
                message=2
            elif message =="relay is STOPPING amplifier, because input power is too high":
                message=3
            else:
                message=4
            arduino.disconnect()
            return message
        
        elif value == 1:
            # print(f'com={i}')
            arduino.connect()
            arduino.reset_relay_latch()
            arduino.disconnect()
            return

        else:
            # This is called when user modifies the keyword
            # Insert some function to execute when user modifies this keyword
            # If it's successful, return 0
            return 0  # return
        
    def LFC_YJ_SHUTTER(self, value=None): #tets r w
        # if test_mode: return
        #return
        arduino = self.__LFC_ARDUINO_connect()

        if value == None:

            arduino.connect()
            self.__sleep(0.1)
            message=arduino.get_YJ_info()
            
            if message in ['YJState\r\r\nYJ shutter is UP, YJ is shutted.']:
                message = 0
            if message in ['YJState\r\r\nYJ shutter is DOWN, YJ is passing.']:
                message = 1
            # fill in read functions
            return message
        
        if value == 1:
            
            # print(f'com={i}')
            arduino.connect()
            arduino.pass_YJ()
            arduino.disconnect()
            return 0 # 1

        elif value == 0:
            arduino.connect()
            arduino.shut_YJ()
            arduino.disconnect()
            return 0  # return
        else:
            return #KTLarray('YJ shutter value =1 or 0')
        
    def LFC_YJ_ONOFF(self, value=None): #test r w
        if test_mode: return
        return self.LFC_YJ_SHUTTER(value)

    def LFC_OSA(self,value=None): #TBD
        if test_mode: return
        osa = self.__LFC_OSA_connect()
        if value == None:
            osa.connect()
            osa.get_wavelength()
            osa.disconnect()
            return
        else:
            return 0


    def LFC_2BY2_SWITCH(self, value=None): #test r w
        if test_mode: return
        # Both keyword read and write are tested!
        # if test_mode: return
        switch = self.__LFC_2BY2_SWITCH_connect()
        if value == None:
            switch.connect()
            state=switch.check_status()
            switch.disconnect()
            print('LFC_2BY2_SWITCH read block called. ', state)
            return state
        else:

            ## YooJung's note:
            ## this keyword is implemented as "Enumerated" keyword. (see LFC.xml.sin in KTL server/)
            ## If the user sets the keyword to the string representation,
            ## KTL will translate it, so the values here are either 1 or 2 only.
            ## Please see the modified codes below.

            if value in [1, 2]: 
                print('LFC_2BY2_SWITCH write block called. Writing', value)

                switch.connect()
                switch.set_status(value)
                self.__sleep(0.5)
                # state=switch.check_status()
                switch.disconnect()   
                # print("Device value:",state)
                return 0 # Return 0 means it's successful.
            return        

            ## original code below:
            if value == 'YJ' or value == 1:
                value = 1
            elif value == 'HK' or value == 2:
                value = 2
            switch.connect()
            switch.set_status(value)
            self.__sleep(0.5)
            state=switch.check_status()
            switch.disconnect()
            return state
        
    def LFC_YJ_HK(self, value=None): #no 
        if test_mode: return
        return self.LFC_2BY2_SWITCH(value)
        
    def LFC_HK_SHUTTER(self, value=None): #read r w
        if test_mode: return
        #return
        hks = self.__LFC_HK_SHUTTER_connect()
        if value == None:
            
            # print(f'com={i}')
            hks.connect()
            state=hks.get_status()
            hks.disconnect()
            return state
        else:
            if value == 1 or value == 'open':
                value = 1
            elif value == 0 or value == 'close':
                value = 0
            hks.connect()
            hks.set_status(value)
            # self.__sleep(0.5)
            # state=hks.get_status()
            hks.disconnect()
            return 0 #state
        
    def LFC_HK_ONOFF(self, value=None):#no
        if test_mode: return
        return self.LFC_HK_SHUTTER(value)
          
    def LFC_VOA1550_ATTEN(self, value=None): #r w
        # Successfully tested!
        if test_mode: return
        voa = self.__LFC_VOA1550_connect()
        if value == None:
            print("VOA1550_ATTEN read block called")
            voa.connect()
            atten=voa.atten_db
            atten=round(atten,2)
            voa.disconnect()
            print('VOA1550_ATTEN value:', atten)
            return atten
        
        elif value == 'default':
            # YooJung's comment: not sure what this is supposed to do
            voa.connect()
            voa.atten_db=60
            self.__sleep(0.5)
            atten=voa.atten_db
            atten=round(atten,2)
            voa.disconnect()
            return atten
        else:
            print("VOA1550_ATTEN write block called, writing value", value)

            voa.connect()
            voa.atten_db=value
            # self.__sleep(0.5)
            # atten=voa.atten_db
            # print("Device value:",atten)
            voa.disconnect()
            return 0 # YooJung's comment: return 0 if successful
            # return atten
        
    def LFC_PMP_ATT(self, value=None):#no
        if test_mode: return
        return self.LFC_VOA1550_ATTEN(value)
        
    def LFC_VOA1310_ATTEN(self, value=None):#r w
        if test_mode: return
        voa = self.__VOA1310_connect()
        if value == None:
            voa.connect()
            atten=voa.atten_db
            atten=round(atten,2)
            voa.disconnect()
            return atten

        elif value == 'default':
            voa.connect()
            voa.atten_db=60
            self.__sleep(0.5)
            atten=voa.atten_db
            atten=round(atten,2)
            voa.disconnect()
            return atten
        else:
            voa.connect()
            voa.atten_db=value
            # self.__sleep(0.5)
            # atten=voa.atten_db
            # atten=round(atten,2)
            voa.disconnect()
            return 0 #atten
        
    def LFC_YJ_ATT(self, value=None):# no
        if test_mode: return
        return self.LFC_VOA1310_ATTEN(value)
        
    def LFC_VOA2000_ATTEN(self, value=None):# rw
        # Successfully tested!
        if test_mode: return
        voa = self.__VOA2000_connect()
        if value == None:
            voa.connect()
            atten=voa.atten_db
            atten=round(atten,2)
            voa.disconnect()
            return atten
        elif value == 'default':
            voa.connect()
            voa.atten_db=60
            self.__sleep(0.5)
            atten=voa.atten_db
            atten=round(atten,2)
            voa.disconnect()
            return atten
        else:
            voa.connect()
            voa.atten_db=value
            self.__sleep(0.5)
            # atten=voa.atten_db
            voa.disconnect()
            # print("Device value:",atten)
            return 0 # YooJung's comment: return 0 if successful
            # return atten
        
    def LFC_HK_ATT(self, value=None):#no
        if test_mode: return
        return self.LFC_VOA2000_ATTEN(value)

    def LFC_IM_LOCK_MODE(self, value=None):#r
        if test_mode: return
        
    
        if value == None:
            srs = self.__LFC_servo_connect()
            srs.connect()
            servo_IM = self.__LFC_IM_LOCK_connect(srs)
            #servo_IM.connect()
            mode=servo_IM.output_mode
            
            if mode in ['PID' ,'pid']:
                mode = 1
            if mode in ['MAN', 'man'] :
                mode = 0
            

            #servo_IM.disconnect()
            srs.disconnect()
            return mode
        else:
            ## Yoojung's note
            ## this could be implemented as "enumerated" keyword
            ## as in LFC_2BY2_SWITCH, such as
            ## value = 1 if user sets to "PID"
            ## value = 0 if user sets to "MAN"
            ## for now leaving it as string keyword
            srs = self.__LFC_servo_connect()
            srs.connect()
            servo_IM = self.__LFC_IM_LOCK_connect(srs)
            #servo_IM.connect()
            if value == 1:
                value = 'pid'
            if value == 0:
                value='man'

            servo_IM.output_mode=value
            #mode=servo_IM.output_mode
            #servo_IM.disconnect()
            srs.disconnect()
            return 0
        
    def LFC_FUNCTION_GEN_STATE(self, value=None):
        if test_mode: return
        fg = self.__LFC_KEYSIGHT_FG_connect()
        if value == None:
            fg.connect()
            state={}
            for i in [1,2]:
                state[i]=fg.get_channel_parameters(i)
            fg.disconnect()
            return KTLarray(state)
        #TBD

    def LFC_PENDULEM_FREQ(self, value=None):
        if test_mode: return
        pen = self.__LFC_PENDULEM_connect()
        if value == None:
            pen.connect()
            self.__sleep(0.5)
            pen.run()
            freq=pen.measFreq(1)
            return freq
        #TBD

        
    def __LFC_IM_LOCK_PARAMETER_SET(self, p_gain,i_gain,offset,setpoint):#TBD
        srs = self.__LFC_servo_connect()
        servo_IM = self.__LFC_IM_LOCK_connect(srs)
    
        servo_IM.connect()
        servo_IM.prop_gain=p_gain
        servo_IM.intg_gain=i_gain
        servo_IM.outoffset=offset
        servo_IM.set_setpoint(setpoint)


        servo_IM.disconnect()
        srs.disconnect()
        return 

    def LFC_OSC_AUTO_SET(self, value=None):#TBD
        if test_mode: return
        osc = self.__LFC_OSC_connect()
        if value == None:
            osc.connect()
            osc.disconnect()
            return


    def LFC_RB_AUTO_LOCK(self, value=None):#TBD
        if test_mode: return
        return
    
    def LFC_IM_AUTO_LOCK(self, value=None):#TBD
        if test_mode: return
        return

    def LFC_WSP_OPTIMIZE(self, value=None):#TBD
        if test_mode: return
        return
    
    def LFC_EDFA27_INPUT_POWER(self, value=None): #r
        if test_mode: return
        amonic27 = self.__LFC_EDFA27_connect()
        if value == None:
            amonic27.connect()
            input_power=amonic27.inputPowerCh1
            amonic27.disconnect()
            return input_power
        else:
            return 0
        
    def LFC_EDFA23_INPUT_POWER(self, value=None):#r
        if test_mode: return
        amonic23 = self.__LFC_EDFA23_connect()
        if value == None:
            amonic23.connect()
            input_power=amonic23.inputPowerCh1
            amonic23.disconnect()
            return input_power
        else:
            return 0
        
    def LFC_ARDUINO_GET_INPUT(self, value=None):  
        if test_mode: return
        arduino = self.__LFC_ARDUINO_connect()
        if value == None:
            arduino.connect()
            input=arduino.get_current_voltage()
            arduino.disconnect()
            return input
        else:
            return 0
        
    def LFC_MINICOMB_AUTO_SETUP(self, value=None):#TBD
        if test_mode: return

        if value == 1:
            self.LFC_RFOSCI_DEFAULT(1)
            self.LFC_RFOSCI_ONOFF(1)

            self.LFC_RFOSCI_MONITOR()

            self.LFC_RFAMP_DEfAULT(1)
            self.LFC_RFAMP_ONOFF(1)

            self.LFC_RFAMP_MONITOR()

            freq=self.LFC_PENDULEM_FREQ(1)

            if np.abs(freq-16e9)<10:

                self.LFC_CLARITY_ONOFF(1)
                #self.LFC_EDFA27_P_DEFAULT(1)
                edfa27input=self.LFC_EDFA27_INPUT_POWER()

                if (edfa27input<5) & (edfa27input>1):
                    self.LFC_EDFA27_AUTO_ON(1)
                    self.LFC_WSP_PHASE(1) #TBD

                    edfa23input=self.LFC_EDFA23_INPUT_POWER()
                    if (edfa23input<10) & (edfa23input>1):
                        self.LFC_EDFA23_AUTO_ON(1)
                        
                        self.LFC_IM_AUTO_LOCK(1)

                        ptamp_input_status=self.LFC_PTAMP_LATCH()

                        if ptamp_input_status==1:
                            return 11
                        if ptamp_input_status==0:
                            return 10
                        else:
                            self.__sendemail('PTAMP input value is not correct')
                    else:
                        self.__sendemail('EDFA23 input power is not correct')
                else:
                    self.__sendemail('EDFA27 input power is not correct')
            else:
                self.__sendemail('Pendulum frequency is not correct')

        return 0








   
    def LFC_WGD_T(self, value=None):#r w
        if test_mode: return

        tec_wvg=self.__LFC_TEC_WVG_connect()
        

        if value == None:
            tec_wvg.connect()
            twvg=tec_wvg.get_temp()
            tec_wvg.disconnect()
            return twvg

        else:
            tec_wvg.connect()
            now_temp=tec_wvg.get_temp()
            set_temp=value

            temp_gap=round(set_temp-now_temp,2)

            int_p=int(temp_gap//0.5 )
            mod=temp_gap % 0.5
            if (int_p>0) or (int_p==0):
                int_p=int_p
            else:
                int_p=np.abs(int_p)-1

            for i in range(1,int_p+1):
                tec_wvg.set_temp(now_temp+i*0.5)
                time.sleep(4)
                print(tec_wvg.get_temp())

            tec_wvg.set_temp(set_temp)
            tec_wvg.disconnect()
            return 0
            time.sleep(8)
            now_temp=tec_wvg.get_temp()
            tec_wvg.disconnect()
            return now_temp

    def LFC_PPLN_T(self, value=None):#r w
        if test_mode: return

        tec_ppln=self.__LFC_TEC_PPLN_connect()
        

        if value == None:
            tec_ppln.connect()
            tppln=tec_ppln.get_temp()
            tec_ppln.disconnect()
            return tppln

        else:
            tec_ppln.connect()
            now_temp=tec_ppln.get_temp()
            set_temp=value

            temp_gap=round(set_temp-now_temp,2)

            int_p=int(temp_gap//0.5 )
            mod=temp_gap % 0.5
            if (int_p>0) or (int_p==0):
                int_p=int_p
            else:
                int_p=np.abs(int_p)-1

            for i in range(1,int_p+1):
                tec_ppln.set_temp(now_temp+i*0.5)
                time.sleep(4)
                print(tec_ppln.get_temp())

            tec_ppln.set_temp(set_temp)
            # time.sleep(8)
            # now_temp=tec_ppln.get_temp()
            tec_ppln.disconnect()
            return 0 #now_temp













    ########## These are just test keywords and functions ############

    def ICECLK_ONOFF(self, value=None):
        '''Turn on / off the clock '''

        if value == None:
            # print('ICECLK_ONOFF read block called. ', self.keywords['ICECLK_ONOFF'])
            return self.keywords['ICECLK_ONOFF']

        else:
            print('ICECLK_ONOFF write block called. Writing', value)
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
            # print('ICECLK read block called. ', self.keywords['ICECLK'])
            return self.keywords['ICECLK']

        else:
            # print('ICECLK write block called. Writing', value)

            return 0

    def ICESTA(self, value=None):
        ''' shows status of the ICE connection'''

        if value == None:
            # print('ICESTA read block called. doing nothing ...')

            return #self.keywords['ICESTA']
        else:
            # print('ICESTA write block called. Writing', value)

            if value == 2: # disconnect command
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
            # print('SHOW_ALL_VAL read block called. doing nothing ...')

            return
        else:
            print('SHOW_ALL_VAL write block called. Writing', value)
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
            # print('ICETEST read block called. ', value_to_return)
            return value_to_return  #self.keywords['ICETEST']

        else:
            print('ICETEST write block called. Writing', value)
            # modify
            #print('modify icetest called')
            return 0
        
    def ICEARRAY(self, value=None):
        '''When called, randomly returns an integer value between 1 to 10'''
        # print('ICEARRAY input value', value)
        if value == None:
            # print('ICEARRAY read block called. doing nothing ...')
            # print(self.keywords['ICEARRAY'])
            return KTLarray(self.keywords['ICEARRAY'])
            # show
            # value_to_return = []
            # import random
            # value_to_return.append(random.randint(1, 10))
            # value_to_return.append(random.random())
            # print('ICEARRAY setting',(value_to_return))
            # return KTLarray(value_to_return)  #self.keywords['ICETEST']

        else:
            print('ICEARRAY write block called. Writing', value)

            # modify
            #print('modify ICEARRAY called')
            return 0


if __name__ == "__main__":
    lfc = KeckLFC()
    #lfc.osa.connect()
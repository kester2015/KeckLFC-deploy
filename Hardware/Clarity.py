from .Device import Device
import numpy as np
import time


class Clarity(Device):

    def __init__(self, addr='ASRL4::INSTR', name="Clarity"):
        super().__init__(addr=addr, name=name, isVISA=True)

        self.inst.timeout = 25000  # communication time-out time set in units of ms
        self.inst.baud_rate = 9600  # baud rate is 9600 by default. THIS SETTING IS NECESSARY for success communication
        self.inst.read_termination = '\r\n'  # read_termination is not specified by default.
        self.inst.write_termination = '\n'  # write_termination is '\r\n' by default.

        # For SN: 806734, the following are the factory settings
        # self.__factory_Cur = 1440 # in unit of 0.1mA
        # self.__factory_T = 20.80 # degC

        # For SN: 806734, the following are the default settings to lock to Rb spectroscopy
        # self.__default_Cur_mA = 150 # in unit of 1mA
        # self.__default_T_C = 19.181 # degC

    def connect(self):
        self.connected = True
        self.info(self.devicename+": connected.")
        print("Clarity connect function is special, it actually do nothing.")

    def auto_on(self):
        self.write('CAL:INT')

    def get_status(self):
        tem=self.query('SYST:STAT?') # 0:off  1:calibrating 2:locking 3:locked
        return int(tem[-1])
    
    def get_onoff(self):
        tem=self.query('SOUR:STAT?')

        if tem[-2:]== 'ON':
            return 1
        if tem[-2:]== 'FF':
            return 0

    def set_onoff(self, onoff):
        
        self.write(f'SOUR:STAT {onoff}')
        time.sleep(0.1)
        return self.get_onoff()
        
    def get_periodic_calibration(self):
        tem=self.query('CALibration:PERiodic?')
        if tem[-2:]== 'FF':
            return 0
        return int(tem[-2:])
    
    def set_periodic_calibration(self, t):
        if t ==0:
            t='OFF'
        self.write(f'CALibration:PERiodic {t}')
        time.sleep(0.1)
        return self.get_periodic_calibration()

    def get_lock_status(self):
        tem=self.query('SYST:Kloc?')
        if tem[-2:]== 'FF':
            return 0
        
        if tem[-2:]== 'ON':
            return 1
        
    def set_lock_status(self, onoff):
        self.write(f'SYST:Kloc {onoff}')
        time.sleep(0.1)
        return self.get_lock_status()

    def set_lock_position(self, pos):  # 0: left 1: center

        if pos == 0:
            self.write('SOUR:FREQ:MODE LEFT')
        if pos == 1:
            self.write('SOUR:FREQ:MODE CENT')

        return
    
    def get_frequency(self):  #THZ

        self.write("SOUR:FREQ?")
        import time
        time.sleep(1)
        aa=self.inst.read(termination = 'THz')
        return float(aa[-11:])

    def get_wavelength(self):

        self.write("SOUR:WAVE?")
        import time
        time.sleep(0.2)
        aa=self.inst.read(termination = 'nm')
        return float(aa[-10:])
    
    def enter_password(self, password=5000):
        self.write(f'SYST:PASS ({password})')
        return 
    
    def set_password(self, pass1,pass2):
        self.write(f'SYST:PASS ({pass1}:{pass2})')
        return












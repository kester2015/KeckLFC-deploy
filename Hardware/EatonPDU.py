
from .Device import Device
import warnings
import time

class EatonPDU(Device):
    def __init__(self, addr='ASRL23::INSTR', name="Eaton PDU epduDC", isVISA=True):
        '''Eaton PDU epduDC'''
        super().__init__(addr=addr, name=name, isVISA=isVISA)
        self.inst.baud_rate = 9600
        # self.inst.read_termination = '\r\n'  # read_termination is not specified by default.
        self.inst.write_termination = '\r\n'  # write_termination is '\r\n' by default.

        self.__username = "kecklfc" # default password is "admin"
        self.__password = "astrocomb" # default password is its serial number # 192.168.0.160
        # self.__password = "H619N29036" # 192.168.0.143
        self.max_login_attempt = 5
        # self.loggedin = False # no longer needed because of loggedin is a property now.
        self.__query_interval = 0.02 # second
        self.passcode = "1127" # need to confirm this passcode if you want to turn on/off any outlet.

        # TODO: Assign outlet name to each outlet.
        self.outlet_name_list = ["Outlet A1", "Outlet A2",
                                 "Outlet A3", "Outlet A4",
                                 "Outlet A5", "Outlet A6",
                                 "Outlet A7", "Outlet A8",
                                 "Outlet A9", "Outlet A10",
                                 "Outlet A11", "Outlet A12",
                                 "Outlet A13", "Outlet A14",
                                 "Outlet A15", "Outlet A16",
                                 "Outlet A17", "Outlet A18",
                                 "Outlet A19", "Outlet A20",
                                 "Outlet A21", "Outlet A22",
                                 "Outlet A23", "Outlet A24",]
        
        self.outlet_name_list = ["Outlet B1", "Outlet B2",
                                "Outlet B3", "Outlet B4",
                                "Outlet B5", "Outlet B6",
                                "Outlet B7", "Outlet B8",
                                "Outlet B9", "Outlet B10",
                                "Outlet B11", "Outlet B12",
                                "Outlet B13", "Outlet B14",
                                "Outlet B15", "Outlet B16",
                                "Outlet B17", "Outlet B18",
                                "Outlet B19", "Outlet B20",
                                "Outlet B21", "Outlet B22",
                                "Outlet B23", "Outlet B24",]
        
    def assign_outlet_name(self):
        '''Assign outlet name to each outlet.'''
        count = self.get_outlet_count()
        if len(self.outlet_name_list) != count:
            raise ValueError(f"The length of outlet_name_list {len(self.outlet_name_list)} should be equal to the number of outlets {count}.")
        for i in range(count):
            self.info(self.devicename+f": Outlet {i+1} friendly name was {self.get_outlet_friendly_name(i+1)}")
            self.set_outlet_friendly_name(i+1, self.outlet_name_list[i])
            time.sleep(self.__query_interval)

    def printStatus(self):
        message = "Eaton PDU Status Summary".center(80, '-') + "\n"
        self.info(message)
        status = self.get_all_status()
        message += f"|\tIPv4 Address: {status['ipv4']}\n"
        message += self.input_system_status_to_str(status['InputSystem'])
        message += self.outlet_system_status_all_to_str(status['OutletSystem'])
        message += "Eaton PDU Status Summary Ends".center(80, '-')
        self.info( "Eaton PDU Status Summary Ends".center(80, '-') )
        return message
    
    def get_all_status(self):
        '''Get all status of all outlets. Return a list of status.'''
        self.test_loggedin(relogin=True)
        status = {}
        status['ipv4'] = self.get_ipv4_address(test_loggedin=False)
        time.sleep(self.__query_interval)
        status['InputSystem'] = self.get_input_system_status()
        status['OutletSystem'] = self.get_outlet_status_all()
        return status

    @property
    def loggedin(self):
        return self.test_loggedin(relogin=False)

    def test_loggedin(self, relogin=False):
        '''Test if the device is logged in. Return True if logged in, False if not.'''
        try:
            self.write("")
            tt = self.inst.read(termination='>')
            self.inst.clear()
            if ('pdu' in tt):
                return True
            else:
                raise ValueError("Not logged in.") # Go to except block.
        except: # Not logged in.
            if not relogin: # If no need to relogin, return False.
                return False
            else: # If need to relogin, try to relogin.
                self.warning(self.devicename+": Not logged in. Try to re-login.")
                self.login()
                if not self.test_loggedin(relogin=False):
                    self.warning(self.devicename+": Re-Login failed.")
                    return False # If relogin failed, return False.
                else:
                    self.info(self.devicename+": Last login expired, re-Login succeed.")
                    return True # If relogin succeed, return True.

    def connect(self, login=True):
        cnt = super().connect()
        if login:
            lgin = self.login()
        return cnt, lgin

    def disconnect(self, logout=True):
        # dcnt = super().disconnect()
        if logout:
            lgot = self.logout()
        dcnt = super().disconnect()
        return dcnt, lgot

    def login(self): # login to the device
        '''Login to the device. Return 1 if succeed, -1 if failed.'''
        if not self.connected:
            raise ConnectionError(self.devicename+": Should connect to device before Login.")
        # self.loggedin = self.test_loggedin() # no longer needed because of loggedin is a property now.
        if self.loggedin:
            self.info(self.devicename + ": Already logged in.")
            return 0
        fail_count = 0
        while fail_count<self.max_login_attempt:
            try:
                self.inst.clear()
                self.write("")
                self.info(self.inst.read(termination='in:'))
                self.write(self.__username)
                self.info(self.inst.read(termination='word:'))
                self.write(self.__password)
                tt = self.inst.read(termination='>')
                self.info(tt)
                if 'pdu' in tt:
                    self.info(self.devicename + ": Login succeed.")
                    # self.loggedin = True # no longer needed because of loggedin is a property now.
                    return 1
                else:
                    fail_count += 1
                    self.info(self.devicename + 
                          f": Login failed. You have {self.max_login_attempt - fail_count} attempts left.")
            except:
                fail_count += 1
                self.info(self.devicename + 
                      f": Login failed. You have {self.max_login_attempt - fail_count} attempts left.")
                import time
                time.sleep(1)
        
        self.info(self.devicename + ": Login Failed.")
        return -1

    def logout(self):
        # self.loggedin = self.test_loggedin() # no longer needed because of loggedin is a property now.
        if not self.loggedin:
            self.info(self.devicename + ": Already logged out.")
            return 0
        # if not self.loggedin:
        #     return 0
        self.write("quit")
        # self.loggedin = False # no longer needed because of loggedin is a property now.
        self.info(self.devicename + ": Logged out.")
        return 1
    
    def decode_oneline_response(self, msg, split='\x07'): 
        '''Decode the response message from the device.
        
        The response message should be in the format of {"Command"+split+"Response"}.

        Can only be used when the response message is one line.
        Example: b'get PDU.OutletSystem.Outlet[1].Current\n\r\x070.038\r\npdu#0>'
        Or: 'get PDU.OutletSystem.Outlet.Count\n\r\x0724\r\n'

        Can NOT be used when the response message is multiple lines.
        Example: 'info Environment.Humidity\n\r\x07Name                                               Unit RO/RW Type\r\n----                                               ---- ----- ----\r\nEnvironment.Humidity                                    RO    Float:0..6553.5\r\n'
        '''
        if type(msg)==bytes:
            msg = msg.decode()
        msg = str(msg)
        tt = msg.split(split)
        if len(tt)<2:
            raise ValueError(self.devicename + ": Response message {"+msg+"} is not valid."
                             + " It should be in the format of {"+"Command "+split+" Response"+"}.")
        cmd = tt[0].strip()
        rsp = tt[1].split('\n')[0].strip()
        return {'cmd':cmd, 'rsp':rsp}
    
    def get_ipv4_address(self, test_loggedin=True):
        '''Get the IPv4 address of the device.'''
        if test_loggedin:
            self.test_loggedin(relogin=True)
        self.inst.clear()
        self.write("get System.Network.IPAddress")
        return self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp']
    
    ## --- Input System --- ##
    def get_input_frequency(self, test_loggedin=True):
        '''Get the input frequency. unit: Hz'''
        if test_loggedin:
            self.test_loggedin(relogin=True)
        self.inst.clear()
        self.write("get PDU.Input[1].Frequency")
        return float(self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp'])
    
    def get_input_phase_count(self, test_loggedin=True):
        '''Get the input phase count.'''
        if test_loggedin:
            self.test_loggedin(relogin=True)
        self.inst.clear()
        self.write("get PDU.Input[1].Phase.Count")
        return int(self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp'])
    
    def check_input_phase_available(self, phase: int, test_loggedin=True):
        '''Check if the input phase is within phase count.'''
        if phase>self.get_input_phase_count(test_loggedin=test_loggedin):
            raise ValueError(self.devicename + f": Input phase {phase} is not available. "
                             + f"Input phase count is {self.get_input_phase_count()}.")
        return True
    
    def get_input_active_power_onphase(self, phase: int =1, test_loggedin=True):
        '''Get the input active power. unit: W'''
        self.check_input_phase_available(phase, test_loggedin=test_loggedin)
        self.inst.clear()
        self.write(f"get PDU.Input[1].Phase[{phase}].ActivePower")
        return float(self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp'])
    
    def get_input_apparent_power_onphase(self, phase: int =1, test_loggedin=True):
        '''Get the input apparent power. unit: VA'''
        self.check_input_phase_available(phase, test_loggedin=test_loggedin)
        self.inst.clear()
        self.write(f"get PDU.Input[1].Phase[{phase}].ApparentPower")
        return float(self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp'])
    
    def get_input_current_onphase(self, phase: int =1, test_loggedin=True):
        '''Get the input current. unit: A'''
        self.check_input_phase_available(phase, test_loggedin=test_loggedin)
        self.inst.clear()
        self.write(f"get PDU.Input[1].Phase[{phase}].Current")
        return float(self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp'])
    
    def get_input_voltage_onphase(self, phase: int =1, test_loggedin=True):
        '''Get the input voltage. unit: V'''
        self.check_input_phase_available(phase, test_loggedin=test_loggedin)
        self.inst.clear()
        self.write(f"get PDU.Input[1].Phase[{phase}].Voltage")
        return float(self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp'])
    
    def get_input_active_power(self, test_loggedin=True):
        '''Get the input active power. unit: W'''
        if test_loggedin:
            self.test_loggedin(relogin=True)
        self.inst.clear()
        self.write("get PDU.Input[1].ActivePower")
        return float(self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp'])
    
    def get_input_apparent_power(self, test_loggedin=True):
        '''Get the input apparent power. unit: VA'''
        if test_loggedin:
            self.test_loggedin(relogin=True)
        self.inst.clear()
        self.write("get PDU.Input[1].ApparentPower")
        return float(self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp'])
    
    def get_input_system_status(self):
        '''Get input system status. Return a dict.'''
        status = {}
        self.test_loggedin(relogin=True)
        status['Frequency_Hz'] = self.get_input_frequency(test_loggedin=False)
        time.sleep(self.__query_interval)
        status['ActivePower_W'] = self.get_input_active_power(test_loggedin=False)
        time.sleep(self.__query_interval)
        status['ApparentPower_VA'] = self.get_input_apparent_power(test_loggedin=False)
        time.sleep(self.__query_interval)
        status['PhaseCount'] = self.get_input_phase_count(test_loggedin=False)
        time.sleep(self.__query_interval)
        for i in range(1, status['PhaseCount']+1):
            status[f'Phase{i}'] = {}
            status[f'Phase{i}']['ActivePower_W'] = self.get_input_active_power_onphase(i, test_loggedin=False)
            time.sleep(self.__query_interval)
            status[f'Phase{i}']['ApparentPower_VA'] = self.get_input_apparent_power_onphase(i, test_loggedin=False)
            time.sleep(self.__query_interval)
            status[f'Phase{i}']['Current_A'] = self.get_input_current_onphase(i, test_loggedin=False)
            time.sleep(self.__query_interval)
            status[f'Phase{i}']['Voltage_V'] = self.get_input_voltage_onphase(i, test_loggedin=False)
            time.sleep(self.__query_interval)
        self.info(self.input_system_status_to_str(status))
        return status
    
    def input_system_status_to_str(self, status: dict):
        message = f"|\tInput System Status of {self.devicename}:\n"
        message += f"|\t\tFrequency: {status['Frequency_Hz']} Hz\n"
        message += f"|\t\tActive Power: {status['ActivePower_W']} W\n"
        message += f"|\t\tApparent Power: {status['ApparentPower_VA']} VA\n"
        message += f"|\t\tPhase Count: {status['PhaseCount']}\n"
        for i in range(1, status['PhaseCount']+1):
            message += f"|\t\t\tPhase {i}:\n"
            message += f"|\t\t\t\tActive Power: {status[f'Phase{i}']['ActivePower_W']} W\n"
            message += f"|\t\t\t\tApparent Power: {status[f'Phase{i}']['ApparentPower_VA']} VA\n"
            message += f"|\t\t\t\tCurrent: {status[f'Phase{i}']['Current_A']} A\n"
            message += f"|\t\t\t\tVoltage: {status[f'Phase{i}']['Voltage_V']} V\n"
        return message
    
    ## --- Statistics System --- ##
    # TODO: Statistics System

    ## --- Outlet System --- ##
    def get_outlet_status(self, outlet: int):
        '''Get outlet status. Return a dict.'''
        self.check_outlet_available(outlet)
        status = {}
        status['PresentStatus'] = self.get_outlet_present_status(outlet, test_loggedin=False, test_available=False)
        time.sleep(self.__query_interval)
        status['Switchable'] = self.get_outlet_switchable(outlet, test_loggedin=False, test_available=False)
        time.sleep(self.__query_interval)
        status['FriendlyName'] = self.get_outlet_friendly_name(outlet, test_loggedin=False, test_available=False)
        time.sleep(self.__query_interval)
        status['Current_A'] = self.get_outlet_current(outlet, test_loggedin=False, test_available=False)
        time.sleep(self.__query_interval)
        status['ActivePower_W'] = self.get_outlet_active_power(outlet, test_loggedin=False, test_available=False)
        time.sleep(self.__query_interval)
        status['ApparentPower_VA'] = self.get_outlet_apparent_power(outlet, test_loggedin=False, test_available=False)
        time.sleep(self.__query_interval)
        status['PowerFactor'] = self.get_outlet_power_factor(outlet, test_loggedin=False, test_available=False)
        time.sleep(self.__query_interval)
        self.info(self.outlet_status_to_str(status))
        return status
    
    def outlet_status_to_str(self, outlet_status: dict):
        message = f"|\t\t\t FriendlyName: {outlet_status['FriendlyName']}\n"
        message += f"|\t\t\t PresentStatus: {outlet_status['PresentStatus']}\n"
        message += f"|\t\t\t Switchable: {outlet_status['Switchable']}\n"
        message += f"|\t\t\t Current: {outlet_status['Current_A']} A\n"
        message += f"|\t\t\t ActivePower: {outlet_status['ActivePower_W']} W\n"
        message += f"|\t\t\t ApparentPower: {outlet_status['ApparentPower_VA']} VA\n"
        message += f"|\t\t\t PowerFactor: {outlet_status['PowerFactor']}\n"
        return message
    
    def get_outlet_status_all(self):
        '''Get outlet status. Return a dict.'''
        status = {}
        status['OutletCount'] = self.get_outlet_count()
        message = f"|\tOutlet System of {self.devicename} Summary:\n"
        message += f"|\tOutlet Count: {status['OutletCount']}\n"
        self.info(message)
        for i in range(1, status['OutletCount']+1):
            self.info(f"|\t\tOutlet {i}:")
            status[f'Outlet{i}'] = self.get_outlet_status(i)
        return status
    
    def outlet_system_status_all_to_str(self, outlet_status_all: dict):
        message = f"|\tOutlet System of {self.devicename} Summary:\n"
        message += f"|\tOutlet Count: {outlet_status_all['OutletCount']}\n"
        for i in range(1, outlet_status_all['OutletCount']+1):
            message += f"|\t\tOutlet {i}:\n"
            message += self.outlet_status_to_str(outlet_status_all[f'Outlet{i}'])
        return message

    def get_outlet_count(self, test_loggedin=True):
        '''Get the number of outlets.'''
        if test_loggedin:
            self.test_loggedin(relogin=True)
        self.inst.clear()
        self.write("get PDU.OutletSystem.Outlet.Count")
        return int(self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp'])
    
    def check_outlet_available(self, outlet: int, test_loggedin=True):
        '''Check if the outlet is within outlet count.'''
        if outlet>self.get_outlet_count(test_loggedin=test_loggedin):
            raise ValueError(self.devicename + f": Outlet {outlet} is not available. "
                             + f"Outlet count is {self.get_outlet_count()}.")
        return True
    
    def get_outlet_friendly_name(self, outlet: int, test_loggedin=True, test_available=True):
        '''Get the friendly name of the outlet.'''
        if test_available:
            self.check_outlet_available(outlet, test_loggedin=test_loggedin)
        self.inst.clear()
        self.write(f"get PDU.OutletSystem.Outlet[{outlet}].iName")
        return self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp']
    
    def set_outlet_friendly_name(self, outlet: int, name: str, test_loggedin=True, test_available=True):
        '''Set the friendly name of the outlet.'''
        # name length limit: 31
        if len(name)>31:
            self.warning(self.devicename + f": Friendly name {name} is too long, will be truncated.")
            name = name[:31]
        if test_available:
            self.check_outlet_available(outlet, test_loggedin=test_loggedin)
        self.inst.clear()
        self.write(f"set PDU.OutletSystem.Outlet[{outlet}].iName {name}")
        self.info(self.devicename + f": Outlet {outlet} friendly name set to {name}.")
        return self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp']
    
    def get_outlet_current(self, outlet: int, test_loggedin=True, test_available=True):
        '''Get the current of the outlet.'''
        if test_available:
            self.check_outlet_available(outlet, test_loggedin=test_loggedin)
        self.inst.clear()
        self.write(f"get PDU.OutletSystem.Outlet[{outlet}].Current")
        return float(self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp'])
    
    def get_outlet_active_power(self, outlet: int, test_loggedin=True, test_available=True):
        '''Get the active power of the outlet.'''
        if test_available:
            self.check_outlet_available(outlet, test_loggedin=test_loggedin)
        self.inst.clear()
        self.write(f"get PDU.OutletSystem.Outlet[{outlet}].ActivePower")
        return float(self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp'])
    
    def get_outlet_apparent_power(self, outlet: int, test_loggedin=True, test_available=True):
        '''Get the apparent power of the outlet.'''
        if test_available:
            self.check_outlet_available(outlet, test_loggedin=test_loggedin)
        self.inst.clear()
        self.write(f"get PDU.OutletSystem.Outlet[{outlet}].ApparentPower")
        return float(self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp'])
    
    def get_outlet_power_factor(self, outlet: int, test_loggedin=True, test_available=True):
        '''Get the power factor of the outlet.'''
        if test_available:
            self.check_outlet_available(outlet, test_loggedin=test_loggedin)
        self.inst.clear()
        self.write(f"get PDU.OutletSystem.Outlet[{outlet}].PowerFactor")
        return float(self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp'])
    
    def get_outlet_present_status(self, outlet: int, test_loggedin=True, test_available=True):
        '''Get the present status of the outlet.'''
        if test_available:
            self.check_outlet_available(outlet, test_loggedin=test_loggedin)
        self.inst.clear()
        self.write(f"get PDU.OutletSystem.Outlet[{outlet}].PresentStatus.SwitchOnOff")
        return int(self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp'])
    
    def check_passcode(self, passcode: str):
        '''Check if the passcode is correct.'''
        return passcode == self.passcode
    
    def get_outlet_switchable(self, outlet: int, test_loggedin=True, test_available=True):
        '''Check if the outlet is switchable.
        0 : The outlet is not switchable
        1 : The outlet is switchable
        It is not dependant of the capability of the ePDU SW or not.
        It's a parameter that the user can set to authorise or not switching
        independently on each outlet
        '''
        if test_available:
            self.check_outlet_available(outlet, test_loggedin=test_loggedin)
        self.inst.clear()
        self.write(f"get PDU.OutletSystem.Outlet[{outlet}].Switchable")
        sw = str(self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp'])
        if sw.casefold() == '1':
            return True
        elif sw.casefold() == '0':
            return False
        else:
            raise ValueError(self.devicename + f": Outlet {outlet} switchable status "+str(sw)+" is not available. Available values: 0|1")

    def set_outlet_switchable(self, outlet: int, switchable: bool):
        '''Set the outlet switchable.
        0 : The outlet is not switchable
        1 : The outlet is switchable
        It is not dependant of the capability of the ePDU SW or not.
        It's a parameter that the user can set to authorise or not switching
        independently on each outlet
        '''
        self.check_outlet_available(outlet)
        self.inst.clear()
        self.write(f"set PDU.OutletSystem.Outlet[{outlet}].Switchable {int(switchable)}")
        return self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp']

    def set_outlet_on(self, outlet: int):
        '''Set the outlet on.'''
        if self.get_outlet_present_status(outlet) == 1:
            self.info(self.devicename + f": Outlet {outlet} is already on.")
            return True
        
        confirm = input(self.devicename + f": Outlet {outlet} is off now.\n"
                        +"Do you want to turn on outlet {outlet}? (y/n)")
        if not confirm.lower() == 'y':
            self.info(self.devicename + f": Outlet {outlet} is not turned on. Turn on is aborted.")
            return False
        passcode = input(self.devicename + f": Please input the passcode to turn on outlet {outlet}: ")
        if not self.check_passcode(passcode):
            self.info(self.devicename + f": Passcode you provided is "+passcode+". Does NOT match preset value. Turn on is aborted.")
            return False
        else:
            self.info(self.devicename + f": Passcode matched preset value. Turn on is continued.")
            return self.__set_outlet_on(outlet)

    def __set_outlet_on(self, outlet: int):
        '''Set the outlet on. This should never be called directly in principle.'''
        if not self.get_outlet_switchable(outlet):
            raise ValueError(self.devicename + f": Outlet {outlet} is not switchable. Turn on is aborted. "+
                             f"Try set outlet switchable by self.set_outlet_switchable({outlet}, True) first.")
        self.inst.clear()
        self.write(f"set PDU.OutletSystem.Outlet[{outlet}].DelayBeforeStartup 0")
        # return self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp']
        time.sleep(self.__query_interval)
        return self.get_outlet_present_status(outlet)
    
    def set_outlet_off(self, outlet: int):
        '''Set the outlet off.'''
        if self.get_outlet_present_status(outlet) == 0:
            self.info(self.devicename + f": Outlet {outlet} is already off.")
            return True
        
        confirm = input(self.devicename + f": Outlet {outlet} is on now.\n"
                        +"Do you want to turn off outlet {outlet}? (y/n)")
        if not confirm.lower() == 'y':
            self.info(self.devicename + f": Outlet {outlet} is not turned off. Turn off is aborted.")
            return False
        passcode = input(self.devicename + f": Please input the passcode to turn off outlet {outlet}: ")
        if not self.check_passcode(passcode):
            self.info(self.devicename + f": Passcode you provided is "+passcode+". Does NOT match preset value. Turn off is aborted.")
            return False
        else:
            self.info(self.devicename + f": Passcode matched preset value. Turn off is continued.")
            return self.__set_outlet_off(outlet)
        
    def __set_outlet_off(self, outlet: int):
        '''Set the outlet off. This should never be called directly in principle.'''
        if not self.get_outlet_switchable(outlet):
            raise ValueError(self.devicename + f": Outlet {outlet} is not switchable. Turn off is aborted. "+
                             f"Try set outlet switchable by self.set_outlet_switchable({outlet}, True) first.")
        self.inst.clear()
        self.write(f"set PDU.OutletSystem.Outlet[{outlet}].DelayBeforeShutdown 0")
        # return self.decode_oneline_response(self.inst.read(termination='pdu#0>'))['rsp']
        time.sleep(self.__query_interval)
        return self.get_outlet_present_status(outlet)




if __name__=="__main__":
    pass
    # eaton = EatonPDU()
    # eaton.connect()
    # eaton.write("get PDU.OutletSystem.Outlet.Count")
    # print(eaton.inst.read(termination='pdu#0>'))
    # eaton.write("set PDU.OutletSystem.Outlet[8].DelayBeforeShutdown 0")
    # print(eaton.inst.read(termination='pdu#0>'))
    # import time
    # time.sleep(5)
    # eaton.write("set PDU.OutletSystem.Outlet[8].DelayBeforeStartup 0")
    # print(eaton.inst.read(termination='pdu#0>'))
    # print(eaton.get_active_power(6))

    # ========== Below are already wrapped functions ==========
    # # eaton.login()
    # eaton.inst.clear()
    # # eaton.write("admin")
    # # eaton.write("H619N29040")
    # eaton.write("")
    # print(eaton.inst.read(termination='in:'))
    # eaton.write("kecklfc")
    # print(eaton.inst.read(termination='word:'))
    # eaton.write("astrocomb")
    # tt = eaton.inst.read(termination='>')
    # print(tt)
    # print('pdu' in tt)
    # eaton.write("get PDU.OutletSystem.Outlet.Count")
    # print(eaton.inst.read(termination='pdu#0>'))
    # eaton.write("quit")
    # # print(eaton.inst.read())
    # # import time
    # # for ii in range(1):
    # #     print(ii)
    # #     eaton.write("")
    # #     # eaton.write("admin")
    # #     # eaton.write("H619N29040")
    # #     print(eaton.inst.read(termination='in:'))

    # #     # eaton.inst.clear()
    # #     time.sleep(0.1)

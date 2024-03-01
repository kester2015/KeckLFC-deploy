from typing import Dict

import numpy as np
import time
from .Device import Device

class InstekGppDCSupply(Device):
    def __init__(self, addr='ASRL5::INSTR', name="Instek GPP DC Power Supply"):
        super().__init__(addr=addr, name=name)
        self.inst.timeout = 25000  # communication time-out time set in units of ms
        self.inst.baud_rate = 115200  # Should be set the same as shown in the device，check at "SYSTEM"->"F1：INTERFACE"
        self.inst.read_termination = '\n'  # read_termination is not specified by default.
        # self.modelNumber = self._IDN.split(',')[1]
        # self.serialNumber = self._IDN.split(',')[2]
        self.__maxISET = 6.200  # max current to be set is 6.200A
        self.__timeout = 3  # time to wait for setting current/voltage. in unit of second

    @property
    def _IDN(self):
        cmd = "*IDN?"
        return self.query(cmd)
    @property
    def modelNumber(self):
        return self._IDN.split(',')[1]
    @property
    def serialNumber(self):
        return self._IDN.split(',')[2]

    def printStatus(self):
        def highlight_status(status_string):
            """Color refer https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal"""
            if status_string in ['UNLOCKED', 'ON']:  # Show a green color
                return "\x1b[1;34;42m" + status_string + "\x1b[0m"
            elif status_string in ['LOCKED', 'OFF']:  # Show a red color
                return "\x1b[1;34;41m" + status_string + "\x1b[0m"
            else:
                return status_string
                
        message = str(self.devicename).center(81,'-')+"\n"
        message = message + "|"+ "Instek GPP DC Power Supply Status Summary".center(80, '-') + "\n"
        message = message + "|"+ ("Model: " + self.modelNumber + ", Serial No." + self.serialNumber).center(80, '-') + "\n"
        message = message + "|\t" + "Channel Summary".center(40, '-') + "\n"
        for chan in [1,2,3,4]:
            try:
                self.__validate_channel(chan)
                message = message + "|\t CHANNEL"+str(chan)+": Activation "+highlight_status(self._getOutputStatus(channel=chan))+".\n"
                message = message + f"|\t\t VSET={self._getVSET(channel=chan):.3f}V, ISET={self._getISET(channel=chan):.3f}A.\n"
                message = message + f"|\t\t VOUT={self._getVOUT(channel=chan):.3f}V, IOUT={self._getIOUT(channel=chan):.3f}A.\n"
                message = message + f"|\t\t Output power: {self._getVOUT(channel=chan)*self._getIOUT(channel=chan):.3f}W.\n"
                message = message + f"|\t\t ---Over Voltage/Current Protection Status:---\n"
                message = message + f"|\t\t OVP Status: " +self._getOVPStatus(channel=chan)+ "\t OCP Status: "+self._getOCPStatus(channel=chan)+ " \n"
                message = message + f"|\t\t OVP Level : " +str(self._getOVP(channel=chan))+" V\t OCP Level : "+str(self._getOCP(channel=chan))+ " A\n"
            except:
                pass                
        message = message + "Instek GPP DC Power Supply Status Summary Ends".center(80, '-') + "\n"
        self.info(message)
        return message

    @property
    def Iset1(self):
        return self._getISET(channel=1)

    @Iset1.setter
    def Iset1(self, current):  # current in units of A
        self._setISET(current, channel=1)

    @property
    def Iout1(self):
        return self._getIOUT(channel=1)

    @property
    def Vset1(self):
        return self._getVSET(channel=1)

    @Vset1.setter
    def Vset1(self, voltage):  # voltage in units of V
        self._setVSET(voltage, channel=1)

    @property
    def Vout1(self):
        return self._getVOUT(channel=1)

    @property
    def Pout1(self):  # channel 1 output power, in unit of Watt
        return self.Vout1 * self.Iout1

    # ------ Xouts should not used as set in principle. ------
    @Iout1.setter
    def Iout1(self, I):
        self.Iset1 = I
    @Vout1.setter
    def Vout1(self, V):
        self.Vset1 = V
    # ------ Above parts added in purpose of code behavior clearity

    @property
    def OVPStatus1(self):
        return self._getOVPStatus(channel=1)

    @OVPStatus1.setter
    def OVPStatus1(self, status):
        self._setOVPStatus(status, channel=1)

    @property
    def OVPLevel1(self):
        return self._getOVP(channel=1)

    @OVPLevel1.setter
    def OVPLevel1(self, voltage):
        self._setOVP(voltage, channel=1)

    @property
    def OCPStatus1(self):
        return self._getOCPStatus(channel=1)

    @OCPStatus1.setter
    def OCPStatus1(self, status):
        self._setOCPStatus(status, channel=1)

    @property
    def OCPLevel1(self):
        return self._getOCP(channel=1)

    @OCPLevel1.setter
    def OCPLevel1(self, current):
        self._setOCP(current, channel=1)

    @property
    def activation1(self):
        return self._getOutputStatus(channel=1)

    @activation1.setter
    def activation1(self, status):  # status choose from 0|1|'on'|'off'
        self._setOutputStatus(status, channel=1)

    # ----------------------------------- Private OVP/OCP SET/GET methods --------------------------------------- #
    def _getOVPStatus(self, channel=1):
        self.__validate_channel(channel)
        cmd = f":OUTP{channel:.0f}:OVP:STAT?"
        return self.query(cmd)

    def _setOVPStatus(self, status, channel=1):
        """ State choose from 0|1|'ON'|'OFF', case insensitive"""
        status_dict: Dict[str, str] = {'0': 'OFF', '1': 'ON'}
        self.__validate_channel(channel)
        status = str(status).casefold()
        if status not in ['0', '1', 'on', 'off']:  # input format control
            raise  # TODO： Add InstrError class to handle exceptions systematically
        if status == 'on':
            status = '1'
        if status == 'off':
            status = '0'  # input formatting finished
        cmd = f":OUTP{channel:.0f}:OVP:STAT " + status
        timer_start = time.time()
        time_out = self.__timeout  # 3 seconds
        while not self._getOVPStatus(channel=channel) == status_dict[status]:
            if time.time() > timer_start + time_out:
                raise RuntimeError(self.devicename + ": " + f"channel {channel:.0f} OVP failed to turn "
                                   + status_dict[status].casefold() + f" in {time_out} seconds")
            self.write(cmd)
        self.info(self.devicename + ": " + f"channel {channel:.0f} OVP is turned " + status_dict[status])

    def _getOVP(self, channel=1):
        self.__validate_channel(channel)
        cmd = f":OUTP{channel:.0f}:OVP?"
        return float(self.query(cmd))

    def _setOVP(self, value, channel=1):
        self.__validate_channel(channel)
        cmd = f":OUTP{channel:.0f}:OVP {value}"
        self.write(cmd)
        self.info(self.devicename + ": " + f"OVP channel {channel:.0f} set to {self._getOVP(channel=channel)}V")

    def _getOCPStatus(self, channel=1):
        self.__validate_channel(channel)
        cmd = f":OUTP{channel:.0f}:OCP:STAT?"
        return self.query(cmd)

    def _setOCPStatus(self, status, channel=1):
        """ State choose from 0|1|'ON'|'OFF', case insensitive"""
        status_dict: Dict[str, str] = {'0': 'OFF', '1': 'ON'}
        self.__validate_channel(channel)
        status = str(status).casefold()
        if status not in ['0', '1', 'on', 'off']:  # input format control
            raise  # TODO： Add InstrError class to handle exceptions systematically
        if status == 'on':
            status = '1'
        if status == 'off':
            status = '0'  # input formatting finished
        cmd = f":OUTP{channel:.0f}:OCP:STAT " + status
        timer_start = time.time()
        time_out = self.__timeout  # 3 seconds
        while not self._getOCPStatus(channel=channel) == status_dict[status]:
            if time.time() > timer_start + time_out:
                raise RuntimeError(self.devicename + ": " + f"channel {channel:.0f} OCP failed to turn "
                                   + status_dict[status].casefold() + f" in {time_out} seconds")
            self.write(cmd)
        self.info(self.devicename + ": " + f"channel {channel:.0f} OCP is turned " + status_dict[status])

    def _getOCP(self, channel=1):
        self.__validate_channel(channel)
        cmd = f":OUTP{channel:.0f}:OCP?"
        return float(self.query(cmd))

    def _setOCP(self, value, channel=1):
        self.__validate_channel(channel)
        cmd = f":OUTP{channel:.0f}:OCP {value}"
        self.write(cmd)
        self.info(self.devicename + ": " + f"OCP channel {channel:.0f} set to {self._getOCP(channel=channel)}V")

    # ----------------------------- Private current/voltage/output SET/GET methods --------------------------------- #
    def _getOutputStatus(self, channel=1):
        """ get channel output state, value will be 'ON'|'OFF' """
        self.__validate_channel(channel)
        cmd = f":OUTP{channel:.0f}:STAT?"
        return self.query(cmd)

    def _setOutputStatus(self, status, channel=1):
        """ State choose from 0|1|'ON'|'OFF', case insensitive"""
        status_dict: Dict[str, str] = {'0': 'OFF', '1': 'ON'}
        self.__validate_channel(channel)
        status = str(status).casefold()
        if status not in ['0', '1', 'on', 'off']:  # input format control
            raise  # TODO： Add InstrError class to handle exceptions systematically
        if status == 'on':
            status = '1'
        if status == 'off':
            status = '0'  # input formatting finished
        cmd = f":OUTP{channel:.0f}:STAT "+status
        timer_start = time.time()
        time_out = self.__timeout  # 3 seconds
        while not self._getOutputStatus(channel=channel) == status_dict[status]:
            if time.time() > timer_start + time_out:
                raise RuntimeError(self.devicename + ": " + f"channel {channel:.0f} output failed to turn "
                                   + status_dict[status].casefold() + f" in {time_out} seconds")
            self.write(cmd)
        self.info(self.devicename + ": " + f"channel {channel:.0f} output is turned " + status_dict[status])

    def _getIOUT(self, channel=1):
        self.__validate_channel(channel)
        cmd = f"IOUT{channel:.0f}?"
        return self.__current_str_to_A(self.query(cmd))

    def _getISET(self, channel=1):
        self.__validate_channel(channel)
        cmd = f"ISET{channel:.0f}?"
        return float(self.query(cmd)) #self.__current_str_to_A(self.query(cmd))

    def _setISET(self, current, channel=1):
        self.__validate_channel(channel)
        if current>self.__maxISET:
            raise ValueError(self.devicename + ": " + f"specified ISET {current}A higher than max {self.__maxISET}A.")
        cmd = f"ISET{channel:.0f}:{current:.3f}"
        timer_start = time.time()
        time_out = self.__timeout  # 3 seconds
        while np.abs(self._getISET(channel=channel)-current) > 0.001:
            if time.time() > timer_start + time_out:
                raise RuntimeError(self.devicename + ": " + f"ISET channel {channel:.0f} to {current:.3f}A failed in {time_out} seconds")
            self.write(cmd)
        self.info(self.devicename + ": " + f"ISET channel {channel:.0f} set to {current:.3f}A")


    def _getVOUT(self, channel=1):
        self.__validate_channel(channel)
        cmd = f"VOUT{channel:.0f}?"
        return self.__current_str_to_A(self.query(cmd))

    def _getVSET(self, channel=1):
        self.__validate_channel(channel)
        cmd = f"VSET{channel:.0f}?"
        return float(self.query(cmd)) #self.__current_str_to_A(self.query(cmd))

    def _setVSET(self, voltage, channel=1):
        self.__validate_channel(channel)
        # if voltage>self.__maxVSET:
        #     raise ValueError(self.devicename + ": " + f"specified ISET {voltage}A higher than max {self.__maxVSET}V.")
        cmd = f"VSET{channel:.0f}:{voltage:.3f}"
        timer_start = time.time()
        time_out = self.__timeout  # 3 seconds
        while np.abs(self._getVSET(channel=channel)-voltage) > 0.001:
            if time.time() > timer_start + time_out:
                raise RuntimeError(self.devicename + ": " + f"VSET channel {channel:.0f} to {voltage:.3f}V failed in {time_out} seconds")
            self.write(cmd)
        self.info(self.devicename + ": " + f"VSET channel {channel:.0f} set to {voltage:.3f}V")

    # ----------------------------------------  Private auxiliary methods ------------------------------------------ #
    def __current_str_to_A(self, current_str: str) -> float:
        if current_str[-2:].casefold() == 'ma' or current_str[-2:].casefold() == 'mv':
            return float(current_str[0:-2])/1000
        elif current_str[-1:].casefold() == 'a' or current_str[-1:].casefold() == 'v':
            return float(current_str[0:-1])
        else:
            raise ValueError(self.devicename + ": " + "Unrecognized current str" + current_str + " while converting.")

    def __validate_channel(self, channel):  # validate specified channel exists in certain model, return True if valid
        if self.modelNumber == 'GPP-1326':
            valid = True if channel in [1] else False
            if not valid:
                raise ValueError(self.devicename + ": " + f"specified channel {channel:.0f} out of range for "
                                 +self.modelNumber+", should choose to be 1.")
        elif self.modelNumber == 'GPP-2323':
            valid = True if channel in [1, 2] else False
            if not valid:
                raise ValueError(self.devicename + ": " + f"specified channel {channel:.0f} out of range for "
                                 +self.modelNumber+", should choose from {1|2}.")
        elif self.modelNumber == 'GPP-3323':
            valid = True if channel in [1, 2, 3] else False
            if not valid:
                raise ValueError(self.devicename + ": " + f"specified channel {channel:.0f} out of range for "
                                 +self.modelNumber+", should choose from {1|2|3}.")
        else:  # elif self.modelNumber == 'GPP-4323':
            valid = True if channel in [1, 2, 3, 4] else False
            if not valid:
                raise ValueError(self.devicename + ": " + f"specified channel {channel:.0f} out of range for "
                                 +self.modelNumber+", should choose from {1|2|3|4}.")
        return valid

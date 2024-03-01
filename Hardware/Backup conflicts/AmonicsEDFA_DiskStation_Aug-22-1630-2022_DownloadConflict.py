from operator import mod
from os import terminal_size
from select import select
from signal import raise_signal
from statistics import mode
from typing import Dict
import warnings
import time
from xml.parsers.expat import model

from .Device import Device
import numpy as np
''' Author: Maodong Gao, version 0.0, Dec 03 2021, tested on AEDFA-PA-30-B-FA, No.21020811 '''
''' PLEASE FOLLOW camelCase Convention to maintain '''


class AmonicsEDFA(Device):

    def __init__(self, addr='ASRL4::INSTR', name="Amonics EDFA"):
        super().__init__(addr=addr, name=name)
        self.__activation_timeout = 3  # time to wait for device to turn on/off activation and channel status. in unit of second.
        self.inst.timeout = 25000  # communication time-out time set in units of ms
        self.inst.baud_rate = 19200  # baud rate is 9600 by default. THIS SETTING IS NECESSARY for success communication
        self.inst.read_termination = '\r\n'  # read_termination is not specified by default.
        self.inst.write_termination = '\r\n'  # write_termination is '\r\n' by default.

    def printStatus(self):

        def highlight_status(status_string):
            """Color refer https://stackoverflow.com/questions/287871/how-to-print-colored-text-to-the-terminal"""
            if status_string in ['UNLOCKED', 'ON']:  # Show a green color
                return "\x1b[1;34;42m" + status_string + "\x1b[0m"
            elif status_string in ['LOCKED', 'OFF']:  # Show a red color
                return "\x1b[1;34;41m" + status_string + "\x1b[0m"
            else:
                return status_string

        message = str(self.devicename).center(81, '-') + "\n"
        message = message + "|" + "Amonics EDFA Status Summary".center(80, '-') + "\n"
        message = message + "|" + ("Model: " + self.modelNumber + ", Serial No." + self.serialNumber).center(80,
                                                                                                             '-') + "\n"
        message = message + "|\tInterLock Status: " + highlight_status(self.interLock) + "\n"
        message = message + "|\tCase Temperature: " + f"{self.caseTemperature:.2f}" + u'\N{DEGREE SIGN}' + "C\n"
        message = message + "|\tMaster Activation: " + highlight_status(self.activation) + "\n"
        message = message + "|\t" + "Channel Summary".center(40, '-') + "\n"
        message = message + "|\t CHANNEL1: \n"
        m = self.modeCh1
        message = message + "|\t\t Mode: " + m + "\n"
        message = message + "|\t\t Set "+("Cur" if m=='ACC' else "Pwr") +": " + str(self.accCh1Cur) + (" mA" if m=='ACC' else " mW")+"\n"
        message = message + "|\t\t Status: " + highlight_status(self.accCh1Status) + "\n"
        message = message + "|\t\t Output Power: " + str(self.outputPowerCh1) + "mW\n"
        message = message + "|\t\t Internal PD Power: " + str(self.PDPowerCh1) + "mW\n"
        message = message + "Amonics EDFA Status Summary Ends".center(80, '-') + "\n"
        print(message)
        return message

    @property
    def interLock(self):
        status_dict: Dict[str, str] = {'0': 'UNLOCKED', '1': 'LOCKED'}
        response = self.query(':DRIV:INTERLOCK?')
        if response not in status_dict:
            raise  # TODO： Add InstrError class to handle exceptions systematically
        return status_dict[response]

    @property
    def caseTemperature(self):
        return float(self.query(':SENS:TEMP:BOX?'))  # in degree C

    @property
    def modeList(self):  # TODO: test this function on a ACC/APC supported model
        response = self.query(':READ:MODE:NAMES?')
        return response

    @property
    def modelNumber(self):
        return self.query(':CAL:SYS:MODEL?')

    @property
    def serialNumber(self):
        return self.query(':CAL:SYS:SERIAL?')

    # ------------------- Channel 1 related methods ------------------- #
    @property
    def outputPowerCh1(self):
        """Get the existing output power value (in mW) of channel 1"""
        return float(self.query(':SENS:POW:OUT:CH1?'))  # in unit of mW

    @property
    def PDPowerCh1(self):
        """Get the existing photo diode power (Internal PD) value (in mW) of channel 1"""
        return float(self.query(':SENS:POW:PD:CH1?'))  # in unit of mW

    @property
    def modeCh1(self):
        try:
            # result =  self.query(':MODE:SW:CH1?')  # SW stands for switch # TODO: This is not passed on AEDFA-PA-30-B-FA
            result = self._getChMode(channel=1)
            # return 'ACC'  # TODO: Debug This why not passed on AEDFA-PA-30-B-FA, No.21020811
            return result
        except:
            return 'ACC'

    @modeCh1.setter
    def modeCh1(self, mode):  # TODO: add input control
        """Switch the laser control mode of channel 1"""
        mode = str(mode).upper()
        if mode not in ['APC', 'ACC']:
            raise ValueError(self.devicename + ": Mode should choose from 'APC'|'ACC', " + mode + "is given.")
        # self.write(':MODE:SW:CH1 ' + mode)
        self._setChMode(mode=mode, channel=1)

    @property
    def accCh1Cur(self):  # in units of mA
        return self._getIorP(channel=1, mode=self.modeCh1)

    @accCh1Cur.setter
    def accCh1Cur(self, cur1):  # cur1 is numeric or str like '0.3A', '250mA'
        cur1 = str(cur1)
        if not cur1.isnumeric():
            cur1 = self.__current_str_to_mA(cur1)
        else:
            cur1 = float(cur1)
        self._setIorP(cur1, channel=1, mode=self.modeCh1)

    @property
    def accCh1Status(self):  # value will be 'OFF'|'ON'|'BUSY'|'LOCK'
        return self._getChStatus(channel=1, mode=self.modeCh1)

    @accCh1Status.setter
    def accCh1Status(self, status):  # status should choose from 0|1|'ON'|'OFF'
        self._setChStatus(status, channel=1, mode=self.modeCh1)

    # ------------------- ENDING of Channel 1 related methods ------------------- #

    # ------------------- Laser MASTER Activation control related methods ------------------- #
    @property
    def activation(self):
        status_dict: Dict[str, str] = {'0': 'OFF', '1': 'ON'}
        re = self.query(':DRIV:MCTRL?')  # MCTRL stand for MasterControl, equivalent to 'Activate' button in front panel
        if re not in status_dict:
            raise  # TODO： Add InstrError class to handle exceptions systematically
        return status_dict[re]

    @activation.setter
    def activation(self, status):
        status_dict: Dict[str, str] = {'0': 'OFF', '1': 'ON'}
        status = str(status).casefold()
        if status not in ['0', '1', 'on', 'off']:  # input format control
            raise  # TODO： Add InstrError class to handle exceptions systematically
        if status == 'on':
            status = '1'
        if status == 'off':
            status = '0'  # input formatting finished
        if status == '1' and self.accCh1Status.casefold() == 'off':
            raise ValueError("Activation can not be turned on when ACC CH1 is OFF. Run self.accCh1Status='on' before "
                             "self.activation='on'")
        if status == '1':  # Give a SAFETY NOTIFY every time before activating
            print(self.devicename + ": " +
                  "ACTIVATING LASER OUTPUT, MAKE SURE SEED INPUT POWER IS APPROPRIATE TO AVOID DAMAGE")
        timer_start = time.time()
        time_out = self.__activation_timeout  # 3 seconds, 2 seconds should be enough according to user manual
        while not self.activation == status_dict[status]:  # If the device is not in desired state,
            if time.time() > timer_start + time_out:
                raise RuntimeError(self.devicename + ": " + f"Activation set failed in {time_out} seconds.")
            print(self.devicename + ": " + "......waiting Activation status set to " + status_dict[status] + ", now " +
                  self.activation)
            self.write(":DRIV:MCTRL " + status)  # Then Continue to send the command
        print(self.devicename + ": " + "setted Activation status as " + self.activation +
              f", finished in {time.time()-timer_start:.3f} seconds")

        # ------------------- ENDING of Laser Activation control related methods ------------------- #

    # ----------------------------- Private current/power/output SET/GET methods --------------------------------- #
    # TODO: Conceal the previous methods private with <channel> and <mode> selection
    # Need test later.
    def _setIorP(self, IorP, channel=1, mode='ACC'):
        # IorP in units of mA or mW!
        cur1 = np.abs(float(IorP))
        mode = str(mode).upper()
        channel = str(channel)
        if not self._getChMode(channel=channel) == mode:
            print(self.devicename + ": Mode assignment discrepancy in Setting IorP. Switching to " + mode + " mode.")
            self._setChMode(channel=channel, mode=mode)
        max_cur = float(self.query(":READ:DRIV:MAX:" + mode + ":CH" + channel + "?"))  # ":READ:DRIV:MAX:APC:CH1?"
        if cur1 > max_cur:
            warnings.warn(self.devicename + ": " + mode + " CH" + channel + " set point " +
                          f"{cur1} is higher than maximum {max_cur} " + ("mA" if mode == 'ACC' else "mW") +
                          f". Maximum value {max_cur} " + ("mA" if mode == 'ACC' else "mW") + " will be set.")
            cur1 = max_cur
        self.write(":DRIV:" + mode + ":CUR:CH" + channel + f" {cur1}")
        check_cur1 = self._getIorP(channel=channel, mode=mode)  # float(self.query(":DRIV:ACC:CUR:CH1?"))
        if np.abs(check_cur1 - cur1) < 0.5:
            if mode == 'ACC':
                print(self.devicename + ": " + "setted ACC mode CH" + channel + f" current as {check_cur1} mA.")
            else:  #mode == 'APC':
                print(self.devicename + ": " + "setted APC mode CH" + channel + f" current as {check_cur1} mW.")
            return 1
        else:
            if mode == 'ACC':
                print(self.devicename + ": " + "setted ACC mode CH" + channel + f" current as {check_cur1} mA.")
                warnings.warn(self.devicename + ": " + "ACC mode CH" + channel +
                              f" current setpoint {cur1} deviates from current value {check_cur1} mA.")
            else:  #mode=='APC'
                print(self.devicename + ": " + "setted APC mode CH" + channel + f" power as {check_cur1} mW.")
                warnings.warn(self.devicename + ": " + "APC mode CH" + channel +
                              f" power setpoint {cur1} deviates from current value {check_cur1} mW.")
            return 0

    def _getIorP(self, channel=1, mode='ACC'):
        mode = str(mode).upper()
        channel = str(channel)
        cur1 = self.query(":DRIV:" + mode + ":CUR:CH" + channel + "?")  #self.query(":DRIV:ACC:CUR:CH1?")
        cur1 = float(cur1)
        unit = self.query(":READ:DRIV:UNIT:" + mode + ":CH" + channel +
                          "?")  #self.query(':READ:DRIV:UNIT:ACC:CH1?')  # Should be mA
        if unit.casefold() in ['ma', 'mw']:
            pass
        elif unit.casefold() in ['a', 'w']:
            cur1 = 1000 * cur1
        # print(self.devicename + ": " + f"getted ACC mode CH1 current as {cur1} mA.")
        return cur1

    def _setChStatus(self, status, channel=1, mode='ACC'):
        mode = str(mode).upper()
        channel = str(channel)
        status_dict: Dict[str, str] = {'0': 'OFF', '1': 'ON', '2': 'BUSY', '4': 'LOCK'}
        status = str(status).casefold()
        if status not in ['0', '1', 'on', 'off']:  # input format control
            raise  # TODO： Add InstrError class to handle exceptions systematically
        if status == 'on':
            status = '1'
        if status == 'off':
            status = '0'  # input formatting finished
        if status == '0' and self.activation.casefold() == 'on':
            warnings.warn(self.devicename + ": " + "Setting " + mode + " CH" + channel +
                          " status OFF while activation ON will automatically OFF the "
                          "activation. Add self.activation='off' before self.accCh1Status='off' ")
        timer_start = time.time()
        time_out = self.__activation_timeout  # 3 seconds
        while not self._getChStatus(channel=channel,
                                    mode=mode) == status_dict[status]:  # If the device is not in desired state,
            if time.time() > timer_start + time_out:
                raise RuntimeError(self.devicename + ": " + "" + mode + " CH" + channel + " status set failed in" +
                                   f" {time_out} seconds.")
            print(self.devicename + ": " + "......waiting " + mode + " CH" + channel + " status set to " +
                  status_dict[status] + ", now " + self._getChStatus(channel=channel, mode=mode))
            self.write(":DRIV:" + mode + ":STAT:CH" + channel + " " + status)  # Then Continue to send the command
        print(self.devicename + ": " + "setted " + mode + " CH" + channel + " status as " +
              self._getChStatus(channel=channel, mode=mode) + f", finished in {time.time()-timer_start:.3f} seconds")

    def _getChStatus(self, channel=1, mode='ACC'):
        mode = str(mode).upper()
        channel = str(channel)
        status_dict: Dict[str, str] = {'0': 'OFF', '1': 'ON', '2': 'BUSY', '4': 'LOCK'}
        response = self.query(":DRIV:" + mode + ":STAT:CH" + channel + "?")
        if response not in status_dict:
            raise  # TODO： Add InstrError class to handle exceptions systematically
        return status_dict[response]

    def _setChMode(self, mode='ACC', channel=1):
        channel = str(channel)
        self.write(':MODE:SW:CH' + channel + ' ' + mode)
        print(self.devicename + ": " + "CH" + channel + " mode set as " + mode)

    def _getChMode(self, channel=1):
        channel = str(channel)
        return self.query(':MODE:SW:CH' + channel + '?')

    # ------ convert units, private method only. -----
    def __current_str_to_mA(self, current_str: str) -> float:
        if current_str[-2:].casefold() in ['ma', 'mv', 'mw']:
            return float(current_str[0:-2])
        elif current_str[-1:].casefold() in ['a', 'v', 'w']:
            return float(current_str[0:-1]) * 1000
        else:
            raise ValueError(self.devicename + ": Unrecognized current str" + current_str + " while converting.")

    # ---- Deprecated methods , already concealed. Delete after stably test concealed APP setting -----
    # @property
    # def accCh1Cur(self):  # in units of mA
    #     """1st stage amplifier current in ACC mode."""

    #     cur1 = self.query(":DRIV:ACC:CUR:CH1?")
    #     cur1 = float(cur1)
    #     unit = self.query(':READ:DRIV:UNIT:ACC:CH1?')  # Should be mA
    #     if unit.casefold() == 'ma':
    #         pass
    #     elif unit.casefold() == 'a':
    #         cur1 = 1000 * cur1
    #     # print(self.devicename + ": " + f"getted ACC mode CH1 current as {cur1} mA.")
    #     return cur1

    # @accCh1Cur.setter
    # def accCh1Cur(self, cur1):
    #     """Set method for accCh1Cur"""

    #     cur1 = np.abs(cur1)
    #     max_cur = float(self.query(':READ:DRIV:MAX:ACC:CH1?'))
    #     if cur1 > max_cur:
    #         warnings.warn(self.devicename + ": " + f"ACC CH1 current set point {cur1} is higher than maximum current {max_cur} mA."
    #                       f" Maximum current {max_cur} mA will be set.")
    #         cur1 = max_cur
    #     self.write(f":DRIV:ACC:CUR:CH1 {cur1}")
    #     check_cur1 = self.accCh1Cur  # float(self.query(":DRIV:ACC:CUR:CH1?"))
    #     if np.abs(check_cur1 - cur1) < 0.5:
    #         print(self.devicename + ": " + f"setted ACC mode CH1 current as {check_cur1} mA.")
    #     else:
    #         print(self.devicename + ": " + f"setted ACC mode CH1 current as {check_cur1} mA.")
    #         warnings.warn(self.devicename + ": " + f"ACC mode CH1 current setpoint {cur1} deviates from current value {check_cur1} mA.")

    # @property
    # def accCh1Status(self):
    #     """ ACC Ch1 status, value will be 'OFF'|'ON'|'BUSY'|'LOCK' """

    #     status_dict: Dict[str, str] = {'0': 'OFF', '1': 'ON', '2': 'BUSY', '4': 'LOCK'}
    #     response = self.query(":DRIV:ACC:STAT:CH1?")
    #     if response not in status_dict:
    #         raise  # TODO： Add InstrError class to handle exceptions systematically
    #     return status_dict[response]

    # @accCh1Status.setter
    # def accCh1Status(self, status):
    #     """ status should choose from 0|1|'ON'|'OFF' """

    #     status_dict: Dict[str, str] = {'0': 'OFF', '1': 'ON', '2': 'BUSY', '4': 'LOCK'}
    #     status = str(status).casefold()
    #     if status not in ['0', '1', 'on', 'off']:  # input format control
    #         raise  # TODO： Add InstrError class to handle exceptions systematically
    #     if status == 'on':
    #         status = '1'
    #     if status == 'off':
    #         status = '0'  # input formatting finished
    #     if status == '0' and self.activation.casefold() == 'on':
    #         warnings.warn(self.devicename + ": " + "Setting ACC CH1 status OFF while activation ON will automatically OFF the "
    #                       "activation. Add self.activation='off' before self.accCh1Status='off' ")
    #     timer_start = time.time()
    #     time_out = self.__activation_timeout  # 3 seconds
    #     while not self.accCh1Status == status_dict[status]:  # If the device is not in desired state,
    #         if time.time() > timer_start + time_out:
    #             raise RuntimeError(self.devicename + ": " + f"ACC CH1 status set failed in {time_out} seconds.")
    #         print(self.devicename + ": " + "......waiting ACC CH1 status set to " + status_dict[
    #             status] + ", now " + self.accCh1Status)
    #         self.write(":DRIV:ACC:STAT:CH1 " + status)  # Then Continue to send the command
    #     print(self.devicename + ": " + "setted ACC CH1 status as " + self.accCh1Status + f", finished in {time.time()-timer_start:.3f} seconds")


if __name__ == '__main__':
    # Following Test cases passed on AEDFA-PA-30-B-FA, No.21020811
    # from LFC.Hardware.AmonicsEDFA import AmonicsEDFA

    # 1. initialization and connection
    print("\n-------------------------------- 1. initialization and connection ---------------------------------------")
    edfa = AmonicsEDFA()  # By default COM4
    edfa.connect()
    print("EDFA Connection status: " + str(edfa.connected))
    edfa.disconnect()
    print("EDFA Connection status: " + str(edfa.connected))
    edfa.connect()  # Leave connection on after 1st test case

    # 2. set and get ch1 current
    print("\n--------------------------------- 2. set and get ch1 current --------------------------------------------")
    edfa.accCh1Cur = 0
    print(edfa.accCh1Cur)
    edfa.accCh1Cur = 0
    edfa.accCh1Cur = 50
    edfa.accCh1Cur = 10000  # Should raise a warning then set to max current
    edfa.accCh1Cur = 0  # set back to 0 after test case for safety

    # 3. turn ch1 on and off
    print("\n-------------------------------------- 3. turn ch1 on and off -------------------------------------------")
    edfa.accCh1Status = 0
    print(edfa.accCh1Status)
    edfa.accCh1Status = 1
    edfa.accCh1Status = 'oFf'  # Should be case insensitive
    edfa.accCh1Status = 'on'
    edfa.accCh1Status = 'off'  # set back to 'off' after test case for safety

    # 4. turn activation on and off
    edfa.accCh1Cur = 0  # set current to 0 before test case for safety
    edfa.accCh1Status = 'on'  # channel 1 should be on before activation on, exception will be tested in next test case
    # # 4.1 turn on and off activation in normal condition (when ch1 is on)
    print(
        "\n------------------------- 4.1 turn on and off activation in normal condition (when ch1 is on) -------------------------"
    )
    print("\n------------------- Setting time should ALL be less than 2 seconds to be robust -------------------------")
    edfa.activation = 1
    edfa.activation = 0
    print(edfa.activation)
    edfa.activation = 'on'
    edfa.activation = 'oFf'  # leave activation to OFF after test case for safety

    # 5. exception tests:
    edfa.accCh1Cur = 0  # set current to 0 before test case for safety
    # 5.1 turn off ch1 when activation is on
    print("\n----------------------------- 5.1 turn off ch1 when activation is on ------------------------------------")
    edfa.accCh1Status = 'on'
    edfa.activation = 'on'
    edfa.accCh1Status = 'off'  # should raise a warning here, activation and ch1 should both be off
    print("CH1 status: " + edfa.accCh1Status)
    print("Activation status: " + edfa.activation)
    # 5.2 turn on activation when ch1 is off
    print("\n---------------------------------- 5.2 turn on activation when ch1 is off -------------------------------")
    edfa.accCh1Status = 'off'
    try:
        edfa.activation = 'on'  # should raise a error
    except ValueError:
        warnings.warn("you try to turn activation on when ch1 is off")
        print("ValueError raised as expected if you try to turn activation on when ch1 is off ")

    # 6. print status
    print("\n-------------------------------------------- 6. print status --------------------------------------------")
    edfa.printStatus()  # TODO: error in get modech1 is bypassed.

    # POST TESTing setting
    print("\n--------------------------------------------- End of Tests ----------------------------------------------")
    edfa.accCh1Cur = 0
    edfa.accCh1Status = 'off'
    edfa.activation = 'off'
    edfa.modeCh1 = 'ACC'

    pass

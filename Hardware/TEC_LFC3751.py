import warnings
import time

from .Device import Device
import numpy as np
''' Author: Maodong Gao, version 0.0, Aug 02 2022 '''


class TEC_LFC3751(Device):

    def __init__(self, addr='ASRL18::INSTR', name="Filter Cavity TEC"):
        super().__init__(addr=addr, name=name)
        self.__RS232_address = '01'  # This can only be set on LFC3751 front panel, range 01-99, '01' is defaulted.
        self.__unit_type = '1'  # 1 = Temperature Controller, 2 = Laser Diode Driver

        self.__default_PID = [30.0, 1.0, 0.0]  # P,I,D respectively
        self.__default_ABC_degC = [10.00, 25.00, 40.00]  # A,B,C respectively. correspond to 19.90, 10.00, 5.326 kOhm
        self.__default_Ilim_pos = 0.0  # Amp, #Must set Ilim_pos to zero, otherwise temperature will increase fast!
        self.__default_Ilim_neg = -0.6  # Amp
        self.__default_Tlim_high = 38.0  # degC
        self.__default_Tlim_low = 18.0  # degC

        self.__query_trial_max = 5  # Num of trials to read before getting the corresponding response to the query cmd code

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
        message = message + "|" + "TEC LFC-3751 Status Summary".center(80, '-') + "\n"
        message = message + "|" + ("Model: " + self.modelNumber + ", Serial No." + self.serialNumber).center(80,
                                                                                                             '-') + "\n"
        message = message + "|\tOutput Status: " + highlight_status(self.output) + "\n"
        message = message + "|\tTE current: " + f"{self.Iact:.2f}" + "A\n"
        message = message + "|\tTemp set: " + f"{self.Tset:.2f}" + u'\N{DEGREE SIGN}' + "C\n"
        message = message + "|\tTemp act: " + f"{self.Tact:.2f}" + u'\N{DEGREE SIGN}' + "C\n"
        message = message + "|\t Limit I: \n"
        message = message + "|\t\t Positive: " + f"{self.Ilim_pos:.2f}" + " A\n"
        message = message + "|\t\t Negative: " + f"{self.Ilim_neg:.2f}" + " A\n"
        message = message + "|\t Limit T: \n"
        message = message + "|\t\t High: " + f"{self.Tlim_high:.2f}" + u'\N{DEGREE SIGN}' + "C\n"
        message = message + "|\t\t Low: " + f"{self.Tlim_low:.2f}" + u'\N{DEGREE SIGN}' + "C\n"
        message = message + "|\t PID parameters: " + str(self.PID) + "\n"
        message = message + "|\t ABC thermistor (" + u'\N{DEGREE SIGN}' + "C): " + str(self.ABC_degC) + "\n"
        message = message + "TEC LFC-3751 Status Summary Ends".center(80, '-') + "\n"
        self.info(message)
        return message

    def Reset_Default(self):
        self.warning(self.devicename +
                     ": To improve code stability, thermistor ABC parameter are not setted in Reset_Default function." +
                     "Also you should not try to set it.")
        time.sleep(0.1)
        self._write_cmd_code(cmd_code=10, data=self.__default_PID[0], read_data=False)
        time.sleep(0.1)
        self._write_cmd_code(cmd_code=11, data=self.__default_PID[1], read_data=False)
        time.sleep(0.1)
        self._write_cmd_code(cmd_code=12, data=self.__default_PID[2], read_data=False)
        time.sleep(0.1)
        self._write_cmd_code(cmd_code=7, data=self.__default_Ilim_pos, read_data=False)
        time.sleep(0.1)
        self._write_cmd_code(cmd_code=8, data=self.__default_Ilim_neg, read_data=False)
        time.sleep(0.1)
        self._write_cmd_code(cmd_code=31, data=self.__default_Tlim_high, read_data=False)
        time.sleep(0.1)
        self._write_cmd_code(cmd_code=32, data=self.__default_Tlim_low, read_data=False)
        time.sleep(0.1)

    @property
    def modelNumber(self):
        return self._query_cmd_code(cmd_code=57)['data']

    @property
    def serialNumber(self):
        return self._query_cmd_code(cmd_code=55)['data']

    @property
    def Tset(self):
        cmd_code = 3
        return float(self._query_cmd_code(cmd_code=cmd_code)['data'])

    @Tset.setter
    def Tset(self, Tset):
        cmd_code = 3
        self._write_cmd_code(cmd_code=cmd_code, data=Tset)
        self.info(self.devicename + ": " + "Temperature setted to " + f"{Tset} degC.")

    @property
    def PID(self):
        pid = [0, 0, 0]
        cmd_code = 10  # P parameter
        pid[0] = float(self._query_cmd_code(cmd_code=cmd_code)['data'])
        cmd_code = 11  # I parameter
        pid[1] = float(self._query_cmd_code(cmd_code=cmd_code)['data'])
        cmd_code = 12  # D parameter
        pid[2] = float(self._query_cmd_code(cmd_code=cmd_code)['data'])
        return pid

#     @PID.setter
#     def PID(self, pid):
#         self._write_cmd_code(cmd_code=10, data=pid[0], read_data=False)
#         time.sleep(0.03)
#         self._write_cmd_code(cmd_code=11, data=pid[1], read_data=False)
#         time.sleep(0.03)
#         self._write_cmd_code(cmd_code=12, data=pid[2], read_data=False)

    @property
    def ABC_degC(self):
        abc = [0, 0, 0]
        abc[0] = float(self._query_cmd_code(cmd_code=21)['data'])
        abc[1] = float(self._query_cmd_code(cmd_code=23)['data'])
        abc[2] = float(self._query_cmd_code(cmd_code=25)['data'])
        return abc

#     @ABC_degC.setter
#     def ABC_degC(self, abc):
#         self._write_cmd_code(cmd_code=21, data=abc[0])
#         time.sleep(0.03)
#         self._write_cmd_code(cmd_code=23, data=abc[1])
#         time.sleep(0.03)
#         self._write_cmd_code(cmd_code=25, data=abc[2])

    @property
    def Tact(self):
        cmd_code = 1
        return float(self._query_cmd_code(cmd_code=cmd_code)['data'])

    @property
    def Iact(self):
        cmd_code = 5
        return float(self._query_cmd_code(cmd_code=cmd_code)['data'])

    @property
    def output(self):
        # To Enable Output or Initiate Autotune: Write data is +XXX.XX1
        # To Disable Output or Abort Autotune: Write data is +XXX.XX0
        # Char 5 = Autotune Error Codes
        #  1 = Zero Value Current Limit Error
        #  2 = Current Limit Cannot reach SET T
        #  3 = Non-uniform TE I step measured
        #  4 = Rate Sign Change
        # Char 4 = Autotune Status [0 = Normal, 1 = Autotune]
        # Char 3 = Decimal Point
        # Char 2 = Temp Limit or Error Limit Status [1 = requires clearing]
        # Char 1 = Integrator Status [0 = OFF, 1 = ON]
        # Char 0 = Output Status [0 = OFF, 1 = ON]

        re = str(int(float(self._query_cmd_code(cmd_code=51)['data']) * 1000 % 10))
        status_dict: Dict[str, str] = {'0': 'OFF', '1': 'ON'}
        if re not in status_dict:
            raise  # TODO： Add InstrError class to handle exceptions systematically
        return status_dict[re]

    @output.setter
    def output(self, status):
        status_dict: Dict[str, str] = {'0': 'OFF', '1': 'ON'}
        status = str(status).casefold()
        if status not in ['0', '1', 'on', 'off']:  # input format control
            raise  # TODO： Add InstrError class to handle exceptions systematically
        if status == 'on':
            status = '1'
        if status == 'off':
            status = '0'  # input formatting finished

        cmd_data = 0.001 if status == '1' else 0

        self._write_cmd_code(cmd_code=51, data=cmd_data, read_data=False)  # Then Continue to send the command
        self.info(self.devicename + ": " + "setted Output status as " + status_dict[status] + ".")

    @property
    def Ilim_pos(self):
        cmd_code = 7
        return float(self._query_cmd_code(cmd_code=cmd_code)['data'])
#     @Ilim_pos.setter
#     def Ilim_pos(self, Ilim_pos):
#         self._write_cmd_code(cmd_code=7, data=Ilim_pos)

    @property
    def Ilim_neg(self):
        cmd_code = 8
        return float(self._query_cmd_code(cmd_code=cmd_code)['data'])
#     @Ilim_neg.setter
#     def Ilim_neg(self, Ilim_neg):
#         self._write_cmd_code(cmd_code=8, data=Ilim_pos)

    @property
    def Tlim_low(self):
        cmd_code = 32
        return float(self._query_cmd_code(cmd_code=cmd_code)['data'])
#     @Tlim_low.setter
#     def Tlim_low(self, Tlim_low):
#         self._write_cmd_code(cmd_code=32, data=Ilim_pos)

    @property
    def Tlim_high(self):
        cmd_code = 31
        return float(self._query_cmd_code(cmd_code=cmd_code)['data'])


#     @Tlim_high.setter
#     def Tlim_high(self, Tlim_high):
#         self._write_cmd_code(cmd_code=31, data=Ilim_pos)

    def _write_cmd_code(self, cmd_code, data=0, read_data=False):
        cmd = self._generate_cmd_packet(cmd_code=cmd_code, data=data, read_data=read_data)
        self.write(cmd)

    def _query_cmd_code(self, cmd_code, data=0, read_data=True):
        cmd = self._generate_cmd_packet(cmd_code=cmd_code, data=data, read_data=read_data)
        response_str = self.query(cmd)
        response = self._decode_response_packet(response_str)
        if not int(response['command_code']) == int(cmd_code):
            count = 0
            while (not int(response['command_code']) == int(cmd_code)) & (count < self.__query_trial_max):
                response_str = self.read()
                response = self._decode_response_packet(response_str)
                count += 1
            if not count < self.__query_trial_max:
                self.warning(self.devicename + ": Query failed to get corresponding response in " +
                             str(self.__query_trial_max) + " times." + " Waiting to get response of cmd code " +
                             str(cmd_code) + ", the last response code is " + str(response['command_code']) +
                             ". Try add time.sleep(1) between commands.")
        return response

    def __getFCS(self, cmd):  # Number used to check the data received and sent
        fcs = 0
        for ss in cmd:
            fcs ^= ord(ss)
        return hex(fcs)[2:]

    def _generate_cmd_packet(self, cmd_code, data=0, read_data=False):
        if cmd_code == 54:
            raise ValueError(self.devicename +
                             ": cmd 54 is password set/read function, which is disabled in this code.")

        # Format data to '000.000', sign will be taken care later.
        data_str = '{0:.3f}'.format(-data if data < 0 else data).zfill(7)
        if data_str > '999.999':
            raise ValueError(self.devicename + ": abs(data) = " + data_str + " over range (<=999.999).")
        # Check cmd_code
        if int(cmd_code) > 99 | int(cmd_code) < 0:
            raise ValueError(self.devicename + ": cmd_code = " + str(cmd_code) + " over range (00<=code<=99).")
        cmd = "!"
        cmd += str(self.__unit_type)
        cmd += str(self.__RS232_address)
        if read_data:  #1 = Read data, 2 = Write data
            cmd += "1"
        else:
            cmd += "2"
        cmd += str(cmd_code).zfill(2)
        if data < 0:
            cmd += "-"
        else:
            cmd += "+"
        cmd += data_str
        cmd += self.__getFCS(cmd)
        return cmd

    def _decode_response_packet(self, response):
        if not response[0] == '@':
            raise ValueError(self.devicename + ": Decode response error. response = " + str(response) +
                             " should start with '@'.")
        if not self.__getFCS(response[:-2]).casefold() == response[-2:].casefold():
            raise ValueError(self.devicename + ": Decode response error. response = " + str(response) +
                             ". Last 2 check sum digit should be " + self.__getFCS(response[:-2]) +
                             ". RS-232 connection might be interrupted during read.")
        result = {}
        result['unit_type'] = response[1]  # 1 = Temperature Controller, 2 = Laser Diode Driver
        result['RS232_address'] = response[
            2:4]  # RS-232 address of the unit as set on the front panel of the unit (00 is reserved)
        result['command_type'] = response[4]  # 1 = Read data, 2 = Write data
        result['command_code'] = response[5:7]
        result['end_code'] = response[7:9]
        result['data'] = response[9:17]
        return result

if __name__ == '__main__':
    pass
import warnings
import time


from .Device import Device
import numpy as np

''' Author: Maodong Gao, version 0.0, Aug 02 2022 '''


class Pizeo_MDT694A(Device):
    def __init__(self, addr='ASRL7::INSTR',name="Filter Cavity Piezo Controller"):
        super().__init__(addr=addr, name=name)
        self.__activation_timeout = 3  # time to wait for device to turn on/off activation and channel status. in unit of second.
        self.inst.timeout = 25000  # communication time-out time set in units of ms
        self.inst.baud_rate = 115200  # baud rate is 9600 by default. THIS SETTING IS NECESSARY for success communication
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

        message = str(self.devicename).center(81,'-')+"\n"
        message = message + "|"+ "Piezo Controller MDT694A Status Summary".center(80, '-') + "\n"
#         message = message + "|"+ ("Model: " + self.modelNumber + ", Serial No." + self.serialNumber).center(80, '-') + "\n"
#         message = message + "|\tInterLock Status: " + highlight_status(self.interLock) + "\n"
#         message = message + "|\tCase Temperature: " + f"{self.caseTemperature:.2f}" + u'\N{DEGREE SIGN}' + "C\n"
#         message = message + "|\tMaster Activation: " + highlight_status(self.activation) + "\n"
#         message = message + "|\t" + "Channel Summary".center(40, '-') + "\n"
#         message = message + "|\t CHANNEL1: \n"
#         message = message + "|\t\t Mode: " + self.modeCh1 + "\n"
#         message = message + "|\t\t Cur/Pow: " + str(self.accCh1Cur) + " mA/mW\n"
#         message = message + "|\t\t Status: " + highlight_status(self.accCh1Status) + "\n"
#         message = message + "|\t\t Output Power: " + str(self.outputPowerCh1) + "mW\n"
#         message = message + "|\t\t Internal PD Power: " + str(self.PDPowerCh1) + "mW\n"
        message = message + "Piezo Controller MDT694A Status Summary Ends".center(80, '-') + "\n"
        self.info(message)
        return message
    
    
    @property
    def Vset(self):
        result = float(self.query("XR?")[6:-1])
        return result
    
    @Vset.setter
    def Vset(self, Vset):
        cmd = f"XV{float(Vset)}"
        self.write(cmd)
        self.info(self.devicename + ": " + "Output voltage setted to "+ f"{Vset} V.")

        
        
        


if __name__ == '__main__':
    
    pass

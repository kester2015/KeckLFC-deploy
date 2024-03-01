
from .Device import Device
import time
import numpy as np

class InstekGPD_4303S(Device):
    def __init__(self, addr='ASRL5::INSTR',name="Instek GPD-4303S DCSupply"):
        super().__init__(addr=addr, name=name)
        self.inst.timeout = 25000  # communication time-out time set in units of ms
        self.inst.baud_rate = 9600  # Should be set the same as shown in the device，4303S use 9600
        self.inst.read_termination = '\r\n'  # read_termination is not specified by default.
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

    @property
    def activation(self):
        if self._getStatusCode()[5] == '0':
            return 'OFF'
        elif self._getStatusCode()[5] == '1':
            return 'ON'
    @activation.setter
    def activation(self, status):  # status choose from 0|1|'on'|'off'
        if str(status).casefold() in ['0', 'off']:
            cmd = "OUT0"
        elif str(status).casefold() in ['1', 'on']:
            cmd = "OUT1"
        else:
            raise ValueError("Instek GPD-4303S DCSupply: specified output status "+str(status)
            +" is not recognized, should choose from {0|1|'on'|'off'}.")
        self.write(cmd)
        self.info("Instek GPD-4303S DCSupply: Output activation is turned " + ("ON." if str(status).casefold() in ['1', 'on'] else "OFF.") )

    @property
    def operationMode(self):
        return self._getOperationMode()
    @operationMode.setter
    def operationMode(self, mode='indep'):
        self._setOperationMode(mode=mode)

    @property
    def Iout1(self):
        return self._getIOUT(channel=1)
    @property
    def Iset1(self):
        return self._getISET(channel=1)
    @Iset1.setter
    def Iset1(self, Iset1):
        self._setISET(current=Iset1, channel=1)
    @property
    def Vout1(self):
        return self._getVOUT(channel=1)
    @property
    def Vset1(self):
        return self._getVSET(channel=1)
    @Vset1.setter
    def Vset1(self, Vset1):
        self._setVSET(voltage=Vset1, channel=1)

    @property
    def Iout2(self):
        return self._getIOUT(channel=2)
    @property
    def Iset2(self):
        return self._getISET(channel=2)
    @Iset2.setter
    def Iset2(self, Iset2):
        self._setISET(current=Iset2, channel=2)
    @property
    def Vout2(self):
        return self._getVOUT(channel=2)
    @property
    def Vset2(self):
        return self._getVSET(channel=2)
    @Vset2.setter
    def Vset2(self, Vset2):
        self._setVSET(voltage=Vset2, channel=2)

    @property
    def Iout3(self):
        return self._getIOUT(channel=3)
    @property
    def Iset3(self):
        return self._getISET(channel=3)
    @Iset3.setter
    def Iset3(self, Iset3):
        self._setISET(current=Iset3, channel=3)
    @property
    def Vout3(self):
        return self._getVOUT(channel=3)
    @property
    def Vset3(self):
        return self._getVSET(channel=3)
    @Vset3.setter
    def Vset3(self, Vset3):
        self._setVSET(voltage=Vset3, channel=3)

    @property
    def Iout4(self):
        return self._getIOUT(channel=4)
    @property
    def Iset4(self):
        return self._getISET(channel=4)
    @Iset4.setter
    def Iset4(self, Iset4):
        self._setISET(current=Iset4, channel=4)
    @property
    def Vout4(self):
        return self._getVOUT(channel=4)
    @property
    def Vset4(self):
        return self._getVSET(channel=4)
    @Vset4.setter
    def Vset4(self, Vset4):
        self._setVSET(voltage=Vset4, channel=4)
    
    # ------ Xouts should not used as set in principle. ------
    @Iout1.setter
    def Iout1(self, I):
        self.Iset1 = I
    @Vout1.setter
    def Vout1(self, V):
        self.Vset1 = V
    @Iout2.setter
    def Iout2(self, I):
        self.Iset2 = I
    @Vout2.setter
    def Vout2(self, V):
        self.Vset2 = V
    @Iout3.setter
    def Iout3(self, I):
        self.Iset3 = I
    @Vout3.setter
    def Vout3(self, V):
        self.Vset3 = V
    @Iout4.setter
    def Iout4(self, I):
        self.Iset4 = I
    @Vout4.setter
    def Vout4(self, V):
        self.Vset4 = V
    # ------ Above parts added in purpose of code behavior clearity

    def setAllZero(self):
        for chan in [1,2,3,4]:
            self._setISET(0,channel=chan)
            self._setVSET(0,channel=chan)
    def setIMaxAll(self):
        self._setISET(3,channel=1)
        self._setISET(3,channel=2)
        self._setISET(1,channel=3) # I3 max=3 if V3<5
        self._setISET(1,channel=4)

    def beep(self, status=1):
        if str(status).casefold() in ['0', 'off']:
            self.write('BEEP0')
            return 0
        elif str(status).casefold() in ['1', 'on']:
            self.write('BEEP0')
            self.write('BEEP1') # turn off then on can give a beep
            return 1
        else:
            raise ValueError("Instek GPD-4303S DCSupply: beep received unrecognized parameter "+
            str(status)+", should choose from { 0 | 1 | 'on' | 'off' }.")

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
        message = message + "|"+ "Instek DC Power Supply GPD-4303S Status Summary".center(80, '-') + "\n"
        message = message + "|"+ ("Model: " + self.modelNumber + ", Serial No." + self.serialNumber).center(80, '-') + "\n"
        message = message + "|\tMaster Activation: " + highlight_status(self.activation) + "\n"
        message = message + "|\t" + "Channel Summary".center(40, '-') + "\n"
        message = message + "|\t CH1: master, CH2: slave, mode " + self.operationMode +'.\n'
        for chan in [1,2,3,4]:
            message = message + "|\t CHANNEL"+str(chan)+": "+self._getChannelMode(chan)+" Mode.\n"
            message = message + f"|\t\t VSET={self._getVSET(channel=chan):.3f}V, ISET={self._getISET(channel=chan):.3f}A.\n"
            message = message + f"|\t\t VOUT={self._getVOUT(channel=chan):.3f}V, IOUT={self._getIOUT(channel=chan):.3f}A.\n"
            message = message + f"|\t\t Output power: {self._getVOUT(channel=chan)*self._getIOUT(channel=chan):.3f}W.\n"
        message = message + "Instek DC Power Supply GPD-4303S Status Summary Ends".center(80, '-') + "\n"
        self.info(message)
        return message

    # ----------------------------- Private current/voltage/output SET/GET methods --------------------------------- #
    def _getStatusCode(self):
        cmd = 'STATUS?' # will return 8 digits of boolean number
        # digit0: CH1 mode, 0: CC, 1: CV. 
        # digit1: CH2 mode, 0: CC, 1: CV. 
        # digit2,3: Tracking mode, 01: independent, 11: series, 10: parallel.
        # digit4: Beep status, 0: off, 1: on.
        # digit5: Output, 0: off, 1: on.
        # digit6,7: N/A (=01 ANYWAY, don't know why CH3,4 are not returned)
        return self.query(cmd)

    def _getChannelMode(self,channel=1):
        self.__validate_channel(channel)
        if channel in [1,2]:
            code = self._getStatusCode()[channel-1] # '0':CC, '1': CV
        else: # channel in [3,4]:
            if np.abs( self._getVOUT(channel=channel)-self._getVSET(channel=channel) )<0.01:
                code = '1'
            else:
                code = '0'
        if code=='1':
            return 'CV'
        elif code=='0':
            return 'CC'
        else:
            return 'UNRECOGNIZED?'

    def _setOperationMode(self, mode='indep'):
        # mode select indep|series|parallel, 
        # 0: Independent
        # 1: Tracking series
        # 2: Tracking parallel
        mode = str(mode).casefold()            
        if mode == 'indep':
            code = 0
        elif mode == 'series':
            code = 1
        elif mode == 'parallel':
            code = 2
        else:
            raise ValueError("Instek GPD-4303S DCSupply: Unrecognized mode "+ mode + "given. Should choose from { 'indep' | 'series' | 'parallel' }")
        cmd = 'TRACK'+str(code)
        self.write(cmd)
        self.info("Instek GPD-4303S DCSupply: operation moe is set to "+mode)

    def _getOperationMode(self):
        code = self._getStatusCode()[2:4]
        if code=='01':
            return 'indep'
        elif code=='11':
            return 'series'
        elif code == '10':
            return 'parallel'
        else:
            return 'UNRECOGNIZED?'

    def _getIOUT(self, channel=1):
        self.__validate_channel(channel)
        cmd = f"IOUT{channel:.0f}?"
        return self.__current_str_to_A(self.query(cmd))

    def _getISET(self, channel=1):
        self.__validate_channel(channel)
        cmd = f"ISET{channel:.0f}?"
        return self.__current_str_to_A(self.query(cmd))

    def _setISET(self, current, channel=1):
        self.__validate_channel(channel)
        if channel in [1,2] and current>3:
            raise ValueError(f"Instek GPD-4303S DCSupply: specified ISET {current}A at CH{channel} higher than max 3A.")
        elif channel in [4] and current>1:
            raise ValueError(f"Instek GPD-4303S DCSupply: specified ISET {current}A at CH{channel} higher than max 1A.")
        elif channel in [3]:
            if current>3:
                raise ValueError(f"Instek GPD-4303S DCSupply: specified ISET {current}A at CH3 higher higher than max: (0-5V,3A)&(5-10V,1A).")
            elif current>1 and self._getVSET(channel=channel)>5:
                raise ValueError(f"Instek GPD-4303S DCSupply: specified ISET {current}A at CH3 higher higher than max: (0-5V,3A)&(5-10V,1A). "+
                "Decrease VSET before this operation! ")
        cmd = f"ISET{channel:.0f}:{current:.3f}"
        timer_start = time.time()
        time_out = self.__timeout  # 3 seconds
        while np.abs(self._getISET(channel=channel)-current) > 0.001:
            if time.time() > timer_start + time_out:
                raise RuntimeError(f"Instek GPD-4303S DCSupply: ISET channel {channel:.0f} to {current:.3f}A failed in {time_out} seconds")
            self.write(cmd)
        self.info(f"Instek GPD-4303S DCSupply: ISET channel {channel:.0f} set to {current:.3f}A")


    def _getVOUT(self, channel=1):
        self.__validate_channel(channel)
        cmd = f"VOUT{channel:.0f}?"
        return self.__current_str_to_A(self.query(cmd))

    def _getVSET(self, channel=1):
        self.__validate_channel(channel)
        cmd = f"VSET{channel:.0f}?"
        return self.__current_str_to_A(self.query(cmd))

    def _setVSET(self, voltage, channel=1):
        self.__validate_channel(channel)
        if channel in [1,2] and voltage>30:
            raise ValueError(f"Instek GPD-4303S DCSupply: specified VSET {voltage}V at CH{channel} higher than max 30V.")
        elif channel in [4] and voltage>5:
            raise ValueError(f"Instek GPD-4303S DCSupply: specified VSET {voltage}V at CH{channel} higher than max 5V.")
        elif channel in [3]:
            if voltage>10:
                raise ValueError(f"Instek GPD-4303S DCSupply: specified VSET {voltage}V at CH3 higher higher than max: (0-5V,3A)&(5-10V,1A).")
            elif voltage>5 and self._getISET(channel=channel)>1:
                raise ValueError(f"Instek GPD-4303S DCSupply: specified VSET {voltage}V at CH3 higher higher than max: (0-5V,3A)&(5-10V,1A). "+
                "Decrease ISET before this operation.")
        cmd = f"VSET{channel:.0f}:{voltage:.3f}"
        timer_start = time.time()
        time_out = self.__timeout  # 3 seconds
        while np.abs(self._getVSET(channel=channel)-voltage) > 0.001:
            if time.time() > timer_start + time_out:
                raise RuntimeError(f"Instek GPD-4303S DCSupply: VSET channel {channel:.0f} to {voltage:.3f}V failed in {time_out} seconds")
            self.write(cmd)
        self.info(f"Instek GPD-4303S DCSupply: VSET channel {channel:.0f} set to {voltage:.3f}V")

    # ----------------------------------------  Private auxiliary methods ------------------------------------------ #
    def __current_str_to_A(self, current_str: str) -> float:
        if current_str[-2:].casefold() == 'ma' or current_str[-2:].casefold() == 'mv':
            return float(current_str[0:-2])/1000
        elif current_str[-1:].casefold() == 'a' or current_str[-1:].casefold() == 'v':
            return float(current_str[0:-1])
        else:
            raise ValueError("Instek GPD-4303S DCSupply: Unrecognized current str "+current_str+", should end with V/A/mV/mA.")

    def __validate_channel(self, channel):  # validate specified channel exists in certain model, return True if valid
        if self.modelNumber == 'GPD-4303S':
            valid = True if channel in [1, 2, 3, 4] else False
            if not valid:
                raise ValueError(f"Instek GPD-4303S DCSupply: specified channel {channel:.0f} out of range for "
                                 +self.modelNumber+", should choose from {1|2|3|4}.")
        else:  # elif self.modelNumber == 'GPP-4323':
            raise ValueError(f"Instek GPD-4303S DCSupply: model number "
            +self.modelNumber+" unrecognized. This class is designed for {GPD-4303S}.")
        return valid


if __name__=="__main__":
    dcsp = InstekGPD_4303S()
    dcsp.connect()

    # print(dcsp.modelNumber)
    # print(dcsp.serialNumber)
    # # dcsp.beep()
    # dcsp.operationMode = 'indep'
    # print(dcsp._getISET(2))
    # dcsp.printStatus()

    # dcsp.beep(0)
    # print(dcsp._getStatusCode())
    # dcsp.beep(1)
    # print(dcsp._getStatusCode())

    # dcsp.operationMode='parallel'
    # print(dcsp._getStatusCode())
    # dcsp.operationMode='series'
    # print(dcsp._getStatusCode())
    # dcsp.operationMode='indep'
    # print(dcsp._getStatusCode())

    # dcsp.activation=0
    # print(dcsp._getStatusCode())
    # dcsp.activation=1
    # print(dcsp._getStatusCode())
    # # dcsp.write('VSET2:')
    # # print(dcsp._getStatusCode())
    # # dcsp.write('OUT0')
    # # print(dcsp._getStatusCode())

    dcsp.setAllZero()
    dcsp.operationMode = 'indep'
    dcsp.Vset2 = 15
    dcsp.Iset2 = 3
    dcsp.activation = 1
    dcsp.printStatus()
    dcsp.activation = 0
    dcsp.printStatus()
    dcsp.beep()
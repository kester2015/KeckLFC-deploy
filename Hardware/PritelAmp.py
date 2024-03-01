import numpy as np
import time
from .Device import Device


class PritelAmp(Device):

    def __init__(self, addr='ASRL6::INSTR', name="Pritel Optical Amplifier"):
        super().__init__(addr, name=name)
        self.inst.timeout = 25000  # communication time-out time set in units of ms
        self.inst.baud_rate = 9600
        self.inst.read_termination = '\n'

        self.__preAmpMax = 600  #mA
        self.__pwrAmpMax = 5800  # 5800 #mA, max 5.8A
        self.__activation_timeout = 5  # time to wait for device to turn on/off activation status. in unit of second.
        self.ramp_pwr_ma = 50  # Ramp up current step, disable by setting self.ramp=0
        self.ramp_pre_ma = 100  # Ramp up current step, disable by setting self.ramp=0

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
        message = message + "|" + "Pritel OPTICAL FIBER AMPLIFIER Status Summary".center(80, '-') + "\n"
        message = message + "|\t Pump status: " + highlight_status(self.activation) + "\n"
        message = message + f"|\t InputPower = {self.inputPwr_mW:.0f} mW, \tPreAmp = {self.preAmp:.0f} mA\n"
        message = message + f"|\t OutputPower = {self.outputPwr_mW/1e3:.2f} W, \tPwrAmp = {self.pwrAmp/1e3:.2f} A\n"
        message = message + "|\t " + self.ASD + "\n"
        message = message + "Pritel OPTICAL FIBER AMPLIFIER Status Summary Ends".center(81, '-') + "\n"
        self.info(message)
        return message

    def query(self, cmd):  # Pritel query need be rewritten!
        time.sleep(0.1)
        super().query(cmd)  # this can only return a blank ''
        time.sleep(0.1)
        response = super().read()
        return str(response)[1:]  # First str is an unknown char, just disgarded.

    def write(self, cmd):  # In principle this should not be used for Pritel
        self.query(cmd)

    def connect(self):
        if not self.connected:
            try:
                self.inst.open()
                self.inst.write("READY?\r")
                time.sleep(1)
                self.inst.clear()
                time.sleep(0.1)
                self.connected = True
                self.info(self.devicename + " connected")
                # response = str(self.read())
                # if response == f"\rPriTel FA Ready":
                #     self.connected = True
                #     self.info(self.devicename + " connected")
                #     return 1
                # else:
                #     self.info(self.devicename + ": Connection Not ready. response: '" + response +"'.")
                #     return -1
            except:
                import sys
                e = sys.exc_info()[0]
                self.error(f"Error:{e}")
                return -1
        return 0

    # @property
    # def ready(self):
    #     return self.query("READY?")

    def easy_turnOn(self, pwr_mA='0.5A', pre_mA='600mA'):
        self.preAmp = pre_mA
        time.sleep(1)
        self.activation = 1
        self.pwrAmp = pwr_mA

    @property
    def preAmp(self):  # in mA
        response = self._getPreAmpStr()  # response = 'PreAmp Current = 000 mA'
        responseEnd = response.split('=')[-1]
        mA = self.__current_str_to_mA(responseEnd)
        return mA

    @preAmp.setter
    def preAmp(self, mA):
        mA = str(mA)
        if not mA.isnumeric():
            if mA.casefold() == 'max':
                mA = self.__preAmpMax
            else:
                mA = self.__current_str_to_mA(mA)
        else:
            mA = float(mA)
        if mA > self.__preAmpMax:
            raise ValueError(self.devicename + f": pwrAmp current {mA} higher than max {self.__preAmpMax} mA")

        # if self.activation.casefold() == 'off':
        #     raise ValueError(self.devicename+": Setting preAmp when activation is OFF is not effective! Run self.activation=1 before setting pwrAmp.")

        # response = self._setPreAmpStr(amp_mA = mA)
        # self.info(self.devicename + ": " + response)
        if self.ramp_pre_ma == 0:
            response = self._setPreAmpStr(amp_mA=mA)
            self.info(self.devicename + ": " + response)
        else:
            self.info(self.devicename + ": " + f"Disable Ramping by self.ramp_pre_ma = 0, now {self.ramp_pre_ma} mA.")
            cur_incr = np.abs(self.ramp_pre_ma)
            now_mA = self.preAmp
            mA_list = np.round(np.linspace(now_mA, mA, max(int(np.ceil(np.abs(now_mA - mA) / cur_incr)), 2)) / 10) * 10
            for cur in mA_list:
                response = self._setPreAmpStr(amp_mA=cur)
                self.info(self.devicename + ": " + response + f", current Output {self.outputPwr_mW/1e3:.2f} W.")

    @property
    def pwrAmp(self):  # in mA
        response = self._getPwrAmpStr()  # response = 'PowerAmp Current = 0.00 A'
        responseEnd = response.split('=')[-1]
        mA = self.__current_str_to_mA(responseEnd)
        return mA

    @pwrAmp.setter
    def pwrAmp(self, mA):
        mA = str(mA)
        if not mA.isnumeric():
            if mA.casefold() == 'max':
                mA = self.__pwrAmpMax
            else:
                mA = self.__current_str_to_mA(mA)
        else:
            mA = float(mA)
        if self.activation.casefold() == 'off':
            self.warning(
                self.devicename +
                ": Setting pwrAmp when activation is OFF is not effective! Run self.activation=1 before setting pwrAmp."
            )
        if mA > self.__pwrAmpMax:
            raise ValueError(self.devicename + f": pwrAmp current {mA} higher than max {self.__pwrAmpMax} mA")
        if self.ramp_pwr_ma == 0:
            response = self._setPwrAmpStr(amp_mA=mA)
            self.info(self.devicename + ": " + response)
        else:
            self.info(self.devicename + ": " + f"Disable Ramping by self.ramp_pwr_ma = 0, now {self.ramp_pwr_ma} mA.")
            cur_incr = np.abs(self.ramp_pwr_ma)
            now_mA = self.pwrAmp
            mA_list = np.round(np.linspace(now_mA, mA, max(int(np.ceil(np.abs(now_mA - mA) / cur_incr)), 2)) / 10) * 10
            for cur in mA_list:
                response = self._setPwrAmpStr(amp_mA=cur)
                self.info(self.devicename + ": " + response + f", current Output {self.outputPwr_mW/1e3:.2f} W.")

    @property
    def outputPwr_mW(self):  # return in mW
        response = self.query("FA OUTPUT?")  # return 'Output Power = 0.00 W'
        responseEnd = response.split('=')[-1]
        mW = self.__current_str_to_mA(responseEnd)
        return mW

    @property
    def inputPwr_mW(self):
        response = self.query("FA INPUT?")  # return 'Input Power = 0 mW'
        responseEnd = response.split('=')[-1]
        mW = self.__current_str_to_mA(responseEnd)
        return mW

    @property
    def ASD(self):  # Auto Shut Down status
        response = self.query("FA ASD?")  # return 'AutoShutDown Enabled. PowerAmp pump current is disabled.'
        return response

    @property
    def activation(self):  # Pump laser, 'ON'|'OFF'
        response = self.query("FA PUMP?")  # return 'Pump OFF'
        responseEnd = response.split(" ")[-1]
        return responseEnd

    @activation.setter
    def activation(self, status):
        status = str(status)
        if not status.casefold() in ['0', '1', 'on', 'off']:
            raise ValueError(self.devicename + ": " + "Activation status " + status +
                             " not recognized. Should choose from 0|1|'ON'|'OFF'. ")
        if status == '0':
            status = 'OFF'
        elif status == '1':
            status = 'ON'
        if status == 'ON':  # Give a SAFETY NOTIFY every time before activating
            self.info(self.devicename + ": " +
                      "ACTIVATING LASER PUMP (OUTPUT), MAKE SURE SEED INPUT POWER IS APPROPRIATE TO AVOID DAMAGE.")
        cmd = "FA " + status
        timer_start = time.time()
        time_out = self.__activation_timeout  # 5 seconds
        while not self.activation.casefold() == status.casefold():
            if time.time() - timer_start > time_out:
                raise RuntimeError(self.devicename + ": " + f"Activation set failed in {time_out} seconds.")
            self.info(self.devicename + ": " + "......waiting Activation status set to " + status + ", now " +
                      self.activation)
            self.query(cmd)
        self.info(self.devicename + ": " + "setted Activation status as " + self.activation +
                  f", finished in {time.time()-timer_start:.3f} seconds")

    # ------ private methods to query and write, will return strings. -------
    def _getPreAmpStr(self):  # return 'PreAmp Current = 000 mA'
        return self.query("FA PREAMP?")

    def _setPreAmpStr(self, amp_mA):  # return 'Setting PreAmp Current to 030 mA'
        amp_mA = float(amp_mA)
        if amp_mA > self.__preAmpMax:  # if >600mA
            raise ValueError(self.devicename + ": preAmp set value " + f"{amp_mA:.0f}".zfill(3) +
                             f" mA higher than max __preAmpMax = {self.__preAmpMax:.0f} mA.")
        cmd = "FA SETPRE " + f"{amp_mA:.0f}".zfill(3)  # command must be 3 digit xxx, set to xxx mA.
        return self.query(cmd)

    def _getPwrAmpStr(self):  # return 'PowerAmp Current = 0.00 A'
        return self.query("FA PWRAMP?")

    def _setPwrAmpStr(self, amp_mA):  # return 'Setting PowerAmp Current to 5.80 A'
        amp_mA = float(amp_mA)
        if not np.mod(amp_mA, 10) == 0:
            self.warning(self.devicename + ": preAmp set value " + f"{amp_mA:.0f}".zfill(3) +
                         f" mA has higher precision than 10mA, will be rounded to " +
                         f"{np.round(amp_mA/10)*10:.0f} mA.")
            amp_mA = np.round(amp_mA / 10) * 10
        if amp_mA > self.__pwrAmpMax:  # if >5800mA
            raise ValueError(self.devicename + ": preAmp set value " + f"{amp_mA:.0f}".zfill(3) +
                             f" mA higher than max __pwrAmpMax = {self.__pwrAmpMax:.0f} mA.")
        cmd = "FA SETPWR " + f"{amp_mA/10:.0f}".zfill(3)  # command must be 3 digit xxx, set to x.xx A.
        return self.query(cmd)

    def __current_str_to_mA(self, current_str: str) -> float:
        if current_str[-2:].casefold() in ['ma', 'mv', 'mw']:
            return float(current_str[0:-2])
        elif current_str[-1:].casefold() in ['a', 'v', 'w']:
            return float(current_str[0:-1]) * 1000
        else:
            raise ValueError(self.devicename + ": Unrecognized current str '" + current_str + "' while converting.")


if __name__ == "__main__":
    amp = PritelAmp()
    amp.connect()
    print(amp.ASD)

    amp.preAmp = '0.2A'
    amp.preAmp = 180
    amp.preAmp = 'Max'

    amp.pwrAmp = '3A'
    amp.pwrAmp = 5000
    amp.pwrAmp = 'Max'
    print(f"PreAmp cur {amp.preAmp} mA")
    print(f"PwrAmp cur {amp.pwrAmp} mA")
    print(f"Input power {amp.inputPwr_mW} mW")
    print(f"Output power {amp.outputPwr_mW} mW")
    amp.preAmp = 0
    amp.pwrAmp = 0

    amp.activation = 0
    print("Pump activation: " + amp.activation)
    amp.activation = 0
    for ii in range(10):
        amp.activation = 0
    amp.printStatus()
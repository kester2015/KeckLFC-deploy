from .Device import Device
import time

class OZopticsVOA(Device):
    def __init__(self, addr='ASRL7::INSTR', name='OZoptics VOA', isVISA=True):
        super().__init__(addr, name, isVISA)
        self.inst.timeout = 25000  # communication time-out time set in units of ms
        self.inst.baud_rate = 9600  # 
        self.inst.read_termination = '\r\n'  # read_termination is not specified by default.
        self.__cmd_interval = 0.1 # in seconds
        self._max_read_line = 32 # Maximum lines to read before 'Done' is read.

    def read(self):
        result = ''
        response = ''
        count = 0
        while not response=='Done':
            if count > self._max_read_line: # defalt 32 lines
                self.warning(self.devicename+ f": read cutoff warning, response 'Done' not detected for more than {self._max_read_line:.0f} read. Increase this limit by: self._max_read_line = 100.")
                return result
            count = count + 1
            if not count==1:
                result = result + response + '\n'
            response = super().read()
        return str(result)

    def query(self, cmd):
        self.inst.clear()
        super().write(cmd)
        return self.read()
    
    def write(self, cmd):
        self.query(cmd)
    
    def printStatus(self):
        message = self.devicename.center(80,'-')+'\n'
        message = message + 'OZ optics VOA Status Summary'.center(80,'-')+'\n'
        message = message + f"|\t Attenuation: {self.atten_db:.2f} (dB)"+'\n'
        time.sleep(0.1)
        message = message + "|\t Device Configure String:" + '\n'
        message = message + "|\t\t" + self._getConfigStr()[:-1].replace('\n','\n|\t\t')
        time.sleep(0.1)
        message = message + '\n'+'OZ optics VOA Status Summary Ends'.center(80,'-')+'\n'
        self.info(message)
        return message

    @property
    def atten_db(self):
        time.sleep(self.__cmd_interval)
        return float(self._getAttenStr().replace('(',':').split((':'))[1])
    
    @atten_db.setter
    def atten_db(self, atten):
        time.sleep(self.__cmd_interval)
        self._setAttenStr(atten_db=atten)

    def _setAttenStr(self, atten_db):
        atten_db = float(atten_db)
        cmd = f"A{atten_db:.2f}"
        str_return = self.query(cmd) # return example: 'Pos:4060'
        self.info(self.devicename+f": VOA attenuation setted to {atten_db:.2f} dB.")
        return str_return

    def _getAttenStr(self):
        cmd = "A?"
        return self.query(cmd) # return example: 'Atten:0.00(dB)'

    def _getConfigStr(self):
        cmd = "CD"
        return self.query(cmd) # return example: 'DD100MC\nV6.2a\nNO:303699-01\nMAX ATTEN:55.00\nOVERSHOOT:-30\nCALIB:MAR-02-2022\nGEAR RATIO:485:1\nMINTERVAL(MS):0.90\nMOTOR VOLT:5\nIL:0.00\nWAVELENGTH:2000\nI2C ADDRESS:64\nW0 2000\n'

    

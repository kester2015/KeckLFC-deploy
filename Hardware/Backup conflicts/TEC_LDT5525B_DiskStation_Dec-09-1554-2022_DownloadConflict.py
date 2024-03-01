
from Device import Device
import time

class TEC_LDT5525B(Device):
    def __init__(self, addr='ASRL33::INSTR', name="PPLN TEC", isVISA=True):
        super().__init__(addr=addr, name=name, isVISA=isVISA)
        self.__read_interval = 0.1 # Interbal to wait before read

        self.inst.timeout = 25000  # communication time-out time set in units of ms
        self.inst.baud_rate = 115200  # baud rate is 9600 by default. THIS SETTING IS NECESSARY for success communication
        self.inst.read_termination = '\n'  # read_termination is not specified by default.
        self.inst.write_termination = '\n'  # write_termination is '\r\n' by default.

    def read(self):
        time.sleep(self.__read_interval)
        return super().read()
    def write(self, cmd):
        time.sleep(self.__read_interval)
        return super().write(cmd)
    def query(self, cmd):
        self.write(cmd=cmd)
        return self.read()

    def printStatus(self):
        print(self.devicename+":...Will add later.")

    @property
    def Tact(self):
        return self.query("TEC:T?")

    @property
    def Tset(self):
        #time.sleep(0.1)
        return self.query("TEC:SET:T?")

    @Tset.setter
    def Tset(self, Tset):
        self.write(f"TEC:T {Tset:.2f}")
    
    @property
    def output(self):
        return self.query("TEC:OUT?")

    @output.setter
    def output(self,act):
        return self.write(f"TEC:OUT {act}")

    @property
    def Ilimit(self):
        return self.query("TEC:LIM:ITE?")
    @

    

    
if __name__=="__main__":
    tec = TEC_LDT5525B()
    tec.connect()
    tec.Tset = 37.4
    print(f"Current set T {tec.Tset}")
    # tec.Tset = 37.4
    #print(f"Current set T {tec.Tset}")

    print(tec.output)
    tec.output=0
    print(tec.output)

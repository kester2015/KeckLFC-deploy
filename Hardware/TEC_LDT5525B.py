from .Device import Device
import time


class TEC_LDT5525B(Device):

    def __init__(self, addr='ASRL33::INSTR', name="PPLN TEC", isVISA=True):
        super().__init__(addr=addr, name=name, isVISA=isVISA)
        self.__read_interval = 0.1  # Interbal to wait before read

        self.inst.timeout = 25000  # communication time-out time set in units of ms
        self.inst.baud_rate = 115200  # baud rate is 9600 by default. THIS SETTING IS NECESSARY for success communication
        self.inst.read_termination = '\n'  # read_termination is not specified by default.
        self.inst.write_termination = '\n'  # write_termination is '\r\n' by default.
        self.__default_Tset = 37.2 # default set up for PPLN to align with Rb absorption feature

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
        self.info(self.devicename + ":...Print status Will add later.")

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
    def output(self, act):
        return self.write(f"TEC:OUT {act}")

    @property
    def Ilimit(self):
        return self.query("TEC:LIM:ITE?")

    @Ilimit.setter
    def Ilimit(self, ii):
        return self.write(f"TEC:LIM:ITE {ii}")

    @property
    def Tlimit(self):
        return self.query("TEC:LIM:THI?")

    @Tlimit.setter
    def Tlimit(self, tt):
        return self.write(f"TEC:LIM:THI {tt}")

    def getMode(self):
        return self.query("TEC:MODE?")

    def setMode(self, mode):
        mode = str(mode).upper()
        if mode == "ITE":
            return self.write("TEC:MODE:ITE")
        elif mode == "R":
            return self.write("TEC:MODE:R")
        elif mode == "T":
            return self.write("TEC:MODE:T")
        else:
            self.warning("wrong mode")


if __name__ == "__main__":
    tec = TEC_LDT5525B()
    tec.connect()
    tec.Tset = 37.4
    print(f"Current set T {tec.Tset}")
    # tec.Tset = 37.4
    #print(f"Current set T {tec.Tset}")

    #print(tec.output)
    tec.output = 0
    print(tec.output)
    tec.Ilimit = 0.9
    print(tec.Ilimit)
    tec.Tlimit = 49.8
    print(tec.Tlimit)
    print(str(tec.getMode))
    print(tec.setMode("T"))

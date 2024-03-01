# from .Device import Device

from pyvisa.constants import VI_ERROR_TMO
from .Device import Device
import time


class PendulumCNT90(Device):
    def __init__(self, addr="GPIB0::10::INSTR",name="Pendulum microwave counter"):
        super().__init__(addr=addr, name=name)
        self.inst.timeout = None
        self.inst.read_termination = '\n'  # read_termination is not specified by default.

        self.__channelDict = {'a': "(@1)", 'b': "(@2)", 'c': "(@3)", '1': "(@1)", '2': "(@2)", '3': "(@3)"}
    
    @property
    def _IDN(self):
        cmd = "*IDN?"
        return self.query(cmd)

    def reset(self):
        confirm = input("Pendulum Freq Counter: Are you sure you want to RESET frequency counter? [Y/N]:")
        if confirm.casefold() == 'y':
            self.write("*RST")

    @property
    def caseTemperature(self):  # temperature at the fan control sensor
        return float(self.query(':SYST:TEMP?'))  # in degree C

    def run(self):
        self.write(":INIT:CONT ON")
        # self.write(":COMF:TOT:CONT")
        self.write(":SENS:TOT:GATE ON")
        self.info("Pendulum Freq Counter: Gate is turned on, measurement result is continuously updated on display.")

    def stop(self):
        self.write(":INIT:CONT OFF")
        # self.write(":COMF:TOT:CONT")
        self.write(":SENS:TOT:GATE OFF")
        self.info("Pendulum Freq Counter: Gate is turned off, measurement result is holded on display.")

    def measFreq(self, chan, measTime=1, measArray=1, log_info=False):  # Measure frequency of channel=chan in unit of Hz
        # measTime in unit of seconds. MeasArray is number of measurements to return
        chan = str(chan).casefold()
        if chan not in self.__channelDict:
            raise ValueError("Pendulum Freq Counter: Unrecognized channel "+ chan +" specified to measure frequency. Should choose from "+ "|".join([*self.__channelDict]) )
        if measTime>1000 or measTime<20e-9:
            raise ValueError("Pendulum Freq Counter: Measurement time should be >20ns(2e-8) and <1000s, "+f"{measTime}s is given.")
        cmd = ":CONF:FREQ " + self.__channelDict[chan]  # example: ":CONF:FREQ @1"
        self.write(cmd)
        self.write(f":ACQ:APER {measTime}")
        self.write(":INIT")  # INIT and FETCh is equivlant to READ
        if measTime>3:
            self.info("Pendulum Freq Counter: channel "+chan+f" frequency measureing, measure time {measTime}s.")
            tosleep = measTime
            while tosleep>0:
                self.info("Pendulum Freq Counter: channel "+chan+" frequency measuring, "+f"......{tosleep} seconds to wait.")
                time.sleep(1)
                tosleep = tosleep - 1
        try:
            result = float(self.query("FETC?"))
        except:
            self.error("Pendulum Freq Counter: Measurement not completed, check signal input.")
            result = -1
        if log_info:
            self.info(f"Pendulum Freq Counter: channel {chan} frequency measured, {result} Hz.")
        return result

# if __name__ == "__main__":

#     mfc = PendulumCNT90()
#     mfc.connect()

#     mfc.write(":CONF:FREQ (@2)")
#     mfc.write(":ACQ:APER 1")

#     # mfc.reset()
#     # print(mfc.query(":MEAS:FREQ? (@2)"))
#     # print(mfc.caseTemperature)
#     print(mfc.measFreq(chan='B', measTime=0.1) / 1e6)

#     print(mfc.query("*IDN?"))

#     mfc.run()
#     mfc.stop()


from nbformat import write
from .Device import Device

class TDS2024C(Device):
    def __init__(self, addr="USB0::0x0699::0x03A6::C031910::INSTR", name="TDS2024C Osc", isVISA=True):
        super().__init__(addr=addr, name=name, isVISA=isVISA)

    def get_trace(self,trace=2):
        self.write("DAT:SOU CH" + str(trace))
        self.write("DAT:ENC ASCI")
        self.write
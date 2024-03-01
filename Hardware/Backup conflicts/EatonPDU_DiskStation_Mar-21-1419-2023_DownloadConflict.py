
from Device import Device


class EatonPDU(Device):
    def __init__(self, addr='ASRL23::INSTR', name="Eaton PDU epduDC	192.168.0.160", isVISA=True):
        super().__init__(addr=addr, name=name, isVISA=isVISA)
        self.inst.baud_rate = 9600
        # self.inst.read_termination = '\r\n'  # read_termination is not specified by default.
        self.inst.write_termination = '\r\n'  # write_termination is '\r\n' by default.

        self.__login = "admin" # default password is "admin"
        self.__password = "H619N29040" # default password is its serial number # 192.168.0.160
        # self.__password = "H619N29036" # 192.168.0.143


if __name__=="__main__":
    eaton = EatonPDU()
    eaton.connect()
    import time
    for ii in range(10):
        print(ii)
        if ii == 6:
            
        print(eaton.read())
        time.sleep(0.1)

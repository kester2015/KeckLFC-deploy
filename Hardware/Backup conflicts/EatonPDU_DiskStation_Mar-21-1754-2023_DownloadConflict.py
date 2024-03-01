
from Device import Device


class EatonPDU(Device):
    def __init__(self, addr='ASRL23::INSTR', name="Eaton PDU epduDC	192.168.0.160", isVISA=True):
        super().__init__(addr=addr, name=name, isVISA=isVISA)
        self.inst.baud_rate = 9600
        # self.inst.read_termination = '\r\n'  # read_termination is not specified by default.
        self.inst.write_termination = '\r\n'  # write_termination is '\r\n' by default.

        self.__username = "kecklfc" # default password is "admin"
        self.__password = "astrocomb" # default password is its serial number # 192.168.0.160
        # self.__password = "H619N29036" # 192.168.0.143
        self.max_login_attempt = 2

    def connect(self, login=True):
        super().connect()
        self.login()

    def login(self):
        if not self.connected:
            raise ConnectionError(self.devicename+": Should connect to device before Login.")

        fail_count = 0
        while fail_count<self.max_login_attempt:
            try:
                self.inst.clear()
                self.write("")
                print(self.inst.read(termination='in:'))
                self.write(self.__username)
                print(self.inst.read(termination='word:'))
                self.write(self.__password)
                tt = self.inst.read(termination='>')
                print(tt)
                if 'pdu' in tt:
                    print(self.devicename + ": Login succeed.")
                    break
                else:
                    fail_count += 1
                    print(self.devicename + 
                          f": Login failed. You have {self.max_login_attempt - fail_count} attempts left.")
            except:
                fail_count += 1
                print(self.devicename + 
                      f": Login failed. You have {self.max_login_attempt - fail_count} attempts left.")
    
    def logout(self):
        self.write("quit")



if __name__=="__main__":
    eaton = EatonPDU()
    eaton.connect()
    # eaton.login()
    eaton.inst.clear()
    # eaton.write("admin")
    # eaton.write("H619N29040")
    eaton.write("")
    print(eaton.inst.read(termination='in:'))
    eaton.write("kecklfc")
    print(eaton.inst.read(termination='word:'))
    eaton.write("astrocomb")
    tt = eaton.inst.read(termination='>')
    print(tt)
    print('pdu' in tt)
    eaton.write("get PDU.OutletSystem.Outlet.Count")
    print(eaton.inst.read(termination='pdu#0>'))
    eaton.write("quit")
    # print(eaton.inst.read())
    # import time
    # for ii in range(1):
    #     print(ii)
    #     eaton.write("")
    #     # eaton.write("admin")
    #     # eaton.write("H619N29040")
    #     print(eaton.inst.read(termination='in:'))

    #     # eaton.inst.clear()
    #     time.sleep(0.1)
